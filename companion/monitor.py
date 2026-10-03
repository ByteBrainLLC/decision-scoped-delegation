# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Deterministic process-local reference-monitor simulation. No real effects.

Only the trusted fixture harness may supply state/administrative events. Hashes
bind bytes within this simulation; they do not authenticate people or endpoints.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from threading import RLock

ROOT = Path(__file__).resolve().parent
RULES = {"R1":"current authority", "R2":"expressed scope", "R3":"retained human decisions", "R4":"bound approvals", "R5":"shared exposure", "R6":"evidence and review", "R7":"recovery and cessation"}

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def model_shape_check(value, schema, path='$'):
    """Checks only this artifact's listed shape keywords. NOT Draft 2020-12 validation."""
    supported={'$schema','$id','title','description','type','const','enum','minimum','maximum','minLength','minItems','uniqueItems','properties','required','additionalProperties','items'}
    if set(schema)-supported: raise ValueError('unsupported shape keyword')
    types={'object':dict,'array':list,'string':str,'integer':int,'number':(int,float),'boolean':bool,'null':type(None)}
    if 'type' in schema:
        candidates=schema['type'] if isinstance(schema['type'],list) else [schema['type']]
        if not any(isinstance(value,types[t]) and not (t in ('integer','number') and isinstance(value,bool)) for t in candidates):
            raise ValueError(path+': wrong type')
    if 'const' in schema and (value != schema['const'] or type(value) is not type(schema['const'])): raise ValueError(path+': const')
    if 'enum' in schema and not any(value==x and type(value) is type(x) for x in schema['enum']): raise ValueError(path+': enum')
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if 'minimum' in schema and value<schema['minimum']: raise ValueError(path+': minimum')
        if 'maximum' in schema and value>schema['maximum']: raise ValueError(path+': maximum')
    if isinstance(value,str) and len(value)<schema.get('minLength',0): raise ValueError(path+': minLength')
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0): raise ValueError(path+': minItems')
        if schema.get('uniqueItems') and len({digest(x) for x in value}) != len(value): raise ValueError(path+': duplicates')
        for n,v in enumerate(value): model_shape_check(v,schema.get('items',{}),f'{path}[{n}]')
    if isinstance(value,dict):
        if set(schema.get('required',[]))-set(value): raise ValueError(path+': missing fields')
        if schema.get('additionalProperties') is False and set(value)-set(schema.get('properties',{})): raise ValueError(path+': unexpected fields')
        for k,v in value.items():
            if k in schema.get('properties',{}): model_shape_check(v,schema['properties'][k],path+'.'+k)

def validate_grant(grant, full_schema=False):
    schema=json.loads((ROOT/'grant.schema.json').read_text())
    if full_schema:
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(grant)
    else: model_shape_check(grant,schema)
    if grant['lifecycle']['expires_at'] <= grant['lifecycle']['not_before']: raise ValueError('empty validity window')
    rc=grant['review_contract']; rung=grant['decision_scope']['book_rung']
    if rc['decision_timing'] != {1:'before_commit',2:'before_commit',3:'within_bounds',4:'retrospective'}[rung]: raise ValueError('rung/decision timing mismatch')
    if rc['sampling']['method']=='all' and rc['sampling']['every_n']!=1: raise ValueError('all sampling must have every_n=1')
    if not {'exposure_total','failure_count'} <= set(rc['aggregate_checks']): raise ValueError('both aggregate checks required in this model')
    ledgers=grant['exposure']['ledgers']
    if len({x['ledger_id'] for x in ledgers})!=len(ledgers): raise ValueError('duplicate ledger IDs')
    for p in grant['pinned_predicates']['predicates']:
        if p['op']=='in' and not isinstance(p['value'],list): raise ValueError('in requires list')
        if p['op']=='lte' and (type(p['value']) is not int or p['value']<0): raise ValueError('lte requires nonnegative integer')
    return True

EFFECT_FIELDS={'effect_id','decision_id','actor_id','grant_id','grant_version','policy_version','configuration_version','decision_class','purpose','operation','resource','recipient','data_class','environment','units','payload','context','reversibility','approval_id'}

def check_effect(e):
    if set(e)!=EFFECT_FIELDS: raise ValueError('effect fields')
    if type(e['units']) is not int or e['units']<0: raise ValueError('units must be nonnegative integer')
    if type(e['grant_version']) is not int or e['grant_version']<1: raise ValueError('invalid version')
    if not isinstance(e['context'],dict) or not isinstance(e['payload'],dict): raise ValueError('payload/context objects required')
    if e['approval_id'] is not None and not isinstance(e['approval_id'],str): raise ValueError('invalid approval ID')
    for k in EFFECT_FIELDS-{'units','grant_version','payload','context','approval_id'}:
        if not isinstance(e[k],str) or not e[k]: raise ValueError('effect string field '+k)
    digest(e)  # reject non-JSON, NaN and infinities

def result(outcome, rule=None, reason='', **extra):
    return dict(outcome=outcome,rule=rule,reason=reason,**extra)

class Monitor:
    def __init__(self,grant):
        self.lock=RLock(); self.now=0
        self.grants={}; self.grant_hashes={}; self.runtime={}; self.roles={}
        self.sponsors={}; self.approvals={}; self.ledgers={}; self.effects={}
        self.audit=[]; self.attempts=[]; self.review_log=[]; self.committed=[]
        self.audit_available=True; self.capabilities={}; self.failure_count=0
        self._install(grant)

    def _install(self,g):
        validate_grant(g); g=deepcopy(g); gid=g['identity']['grant_id']
        if gid in self.grants: raise ValueError('grant IDs immutable; use fresh version identity')
        # Verify ledger conflicts before installing any part of the record.
        for ld in g['exposure']['ledgers']:
            if ld['ledger_id'] in self.ledgers:
                old=self.ledgers[ld['ledger_id']]
                if any(old[k]!=ld[k] for k in ('limit_units','aggregation_scope','epoch')): raise ValueError('ledger cannot reset on grant creation')
        self.grants[gid]=g; self.grant_hashes[gid]=digest(g)
        self.runtime[gid]={'state':g['lifecycle']['initial_state'],'fence':0,'policy_version':g['identity']['policy_version'],'configuration_version':g['identity']['configuration_version'],'review_due_at':self.now+g['review_contract']['cadence_ticks'],'commit_count':0,'pending_samples':[]}
        for hid in [g['issuer']['human_id'],*g['approvals']['approver_ids'],*g['review_contract']['reviewer_ids']]: self.roles.setdefault(hid,True)
        self.sponsors.setdefault(g['identity']['actor_id'],{'human_id':g['sponsor']['human_id'],'accepted':True,'standing':True,'present':True,'coverage_valid':False,'can_inspect':True,'can_halt':True,'can_refuse':True,'acceptance_ref':g['sponsor']['acceptance_ref'],'independence_attestation':deepcopy(g['sponsor']['independence_attestation'])})
        self.capabilities.setdefault(g['recovery']['capability_ref'],True)
        for ld in g['exposure']['ledgers']:
            self.ledgers.setdefault(ld['ledger_id'],dict(ld,committed=0,reservations={}))

    def chain(self,gid):
        out=[]; seen=set()
        while gid is not None:
            if gid in seen or gid not in self.grants: raise ValueError('missing or cyclic chain')
            seen.add(gid); g=self.grants[gid]; out.append(g); gid=g['identity']['parent_grant_id']
        return list(reversed(out))

    def derive(self,child):
        """Instantiate only an accepted, human-preauthorized restriction template."""
        with self.lock:
            try:
                validate_grant(child); p=child['identity']['parent_grant_id']; chain=self.chain(p)
                for a in chain:
                    d=a['derivation']
                    if child['identity']['actor_id'] not in d['allowed_actor_ids'] or child['sponsor']['human_id'] not in d['allowed_sponsor_ids']: return result('deny','R1','child or sponsor outside accepted template')
                    if len(chain)>d['max_depth']: return result('deny','R1','derivation depth')
                    if child['principal']!=a['principal'] or child['identity']['workflow_id']!=a['identity']['workflow_id'] or child['issuer']!=a['issuer']: return result('deny','R2','lineage authority mismatch')
                    if self.runtime[a['identity']['grant_id']]['state']!='active': return result('deny','R1','inactive ancestor')
                self._install(child)
                return result('allow',reason='derived restriction registered')
            except (ValueError,KeyError,TypeError) as exc: return result('deny','R1',str(exc))

    def approve(self,e,approver='human-issuer',expires_at=50,approval_id='A1'):
        """Trusted human-decision input, not an identity-verification implementation."""
        with self.lock:
            check_effect(e)
            if approval_id in self.approvals: raise ValueError('approval IDs cannot be overwritten')
            self.approvals[approval_id]={'authenticated':True,'approver_id':approver,'effect_id':e['effect_id'],'payload_digest':digest({k:v for k,v in e.items() if k!='approval_id'}),'chain_versions':{g['identity']['grant_id']:[g['identity']['version'],self.runtime[g['identity']['grant_id']]['policy_version']] for g in self.chain(e['grant_id'])},'expires_at':expires_at,'claimed_by':None}

    def _check(self,e,existing=None):
        try: check_effect(e); chain=self.chain(e['grant_id'])
        except (ValueError,KeyError,TypeError): return result('deny','R1','malformed effect or lineage')
        leaf=chain[-1]; ident=leaf['identity']
        if e['actor_id']!=ident['actor_id'] or e['grant_version']!=ident['version']: return result('deny','R1','actor or grant version')
        if e['policy_version']!=self.runtime[ident['grant_id']]['policy_version'] or e['configuration_version']!=self.runtime[ident['grant_id']]['configuration_version']: return result('escalate','R1','stale policy or configuration')
        for g in chain:
            gid=g['identity']['grant_id']; rt=self.runtime[gid]; life=g['lifecycle']
            if digest(g)!=self.grant_hashes[gid]: return result('deny','R1','immutable grant changed')
            if rt['state']!='active' or not life['not_before']<=self.now<life['expires_at']: return result('deny','R1','inactive or expired authority')
            if not self.roles.get(g['issuer']['human_id'],False): return result('deny','R1','issuer standing invalid')
            sp=self.sponsors.get(g['identity']['actor_id'],{})
            if not sp.get('accepted') or not sp.get('standing') or not (sp.get('present') or sp.get('coverage_valid')):
                rt['state']='suspended'; rt['fence']+=1
                return result('deny','R1','sponsorship unavailable; suspended')
            # A trusted accepted successor may replace the originally recorded sponsor.
            if sp['independence_attestation']['expires_at']<=self.now: return result('escalate','R1','sponsor attestation expired')
            if g is not leaf:
                if e['actor_id'] not in g['derivation']['allowed_actor_ids']: return result('deny','R1','descendant actor not eligible')
                if self.sponsors[e['actor_id']]['human_id'] not in g['derivation']['allowed_sponsor_ids']: return result('deny','R1','descendant sponsor not eligible')
            if existing and existing['fences'].get(gid)!=rt['fence']: return result('deny','R1','stale commit fence')
        for g in chain:
            if e['decision_class']!=g['decision_scope']['decision_class']: return result('deny','R2','decision class outside scope')
            fields={'operation':'operations','resource':'resources','recipient':'recipients','data_class':'data_classes','environment':'environments','purpose':'purposes'}
            for field,allowed in fields.items():
                if e[field] not in g['permitted_effects'][allowed]: return result('deny','R2',field+' outside inherited scope')
            at=g['pinned_predicates']['alignment_attestation']
            if at['status']=='mismatch': return result('escalate','R2','known intent/predicate mismatch; held')
            if at['status']!='aligned' or at['expires_at']<=self.now: return result('escalate','R2','intent alignment unestablished')
            for p in g['pinned_predicates']['predicates']:
                value=e
                for key in p['field'].split('.'):
                    if not isinstance(value,dict) or key not in value: return result('escalate','R2','mandatory predicate unknown: '+p['field'])
                    value=value[key]
                ok=(type(value) is type(p['value']) and value==p['value']) if p['op']=='eq' else (value in p['value'] if p['op']=='in' else type(value) is int and value<=p['value'])
                if not ok: return result('deny','R2','pinned predicate false: '+p['field'])
        for g in chain:
            if e['operation'] in g['decision_scope']['human_reserved_operations']: return result('deny','R3','governing decision remains human')
        if e['reversibility']!='restorable' and any(g['decision_scope']['book_rung']==4 for g in chain):
            return result('escalate','R3','rung 4 requires reversibility; human-chosen exact execution needs a suitable grant')
        needed=[g for g in chain if g['approvals']['required'] or g['decision_scope']['book_rung'] in (1,2) or e['reversibility']=='irreversible']
        if needed:
            ap=self.approvals.get(e['approval_id'])
            if not ap: return result('escalate','R4','human decision required')
            if not ap['authenticated'] or not self.roles.get(ap['approver_id'],False): return result('deny','R4','approval not authenticated or role invalid')
            if ap['effect_id']!=e['effect_id'] or ap['payload_digest']!=digest({k:v for k,v in e.items() if k!='approval_id'}): return result('escalate','R4','approval payload or target differs')
            if self.now>=ap['expires_at']: return result('escalate','R4','approval expired')
            if ap['claimed_by'] not in (None,e['effect_id']): return result('deny','R4','approval already claimed')
            for g in chain:
                gid=g['identity']['grant_id']
                if ap['chain_versions'].get(gid)!=[g['identity']['version'],self.runtime[gid]['policy_version']]: return result('escalate','R4','approval policy version differs')
            for g in needed:
                if ap['approver_id'] not in g['approvals']['approver_ids']: return result('deny','R4','approver not authorized')
                if g['approvals']['separation_from_issuer'] and ap['approver_id']==g['issuer']['human_id']: return result('deny','R4','separation of duties')
        ledger_ids=set()
        for g in chain:
            if e['units']>g['exposure']['per_effect_units']: return result('deny','R5','per-effect bound exceeded')
            ledger_ids.update(ld['ledger_id'] for ld in g['exposure']['ledgers'])
        for lid in sorted(ledger_ids):
            ld=self.ledgers[lid]; reserved=sum(ld['reservations'].values()); own=ld['reservations'].get(e['effect_id'],0)
            if ld['committed']+reserved+e['units']-own>ld['limit_units']: return result('deny','R5','shared exposure would exceed '+lid)
            if existing and own!=e['units']: return result('deny','R5','reservation missing or changed')
        if not self.audit_available: return result('escalate','R6','pre-effect evidence store unavailable')
        for g in chain:
            gid=g['identity']['grant_id']; rt=self.runtime[gid]
            if self.now>=rt['review_due_at']:
                rt['state']='suspended'; rt['fence']+=1
                return result('escalate','R6','review deadline lapsed; suspended')
            if not any(self.roles.get(h,False) for h in g['review_contract']['reviewer_ids']): return result('escalate','R6','no current reviewer')
        for g in chain:
            gid=g['identity']['grant_id']; rt=self.runtime[gid]
            sp=self.sponsors[g['identity']['actor_id']]
            if not all(sp.get(k) for k in ('can_inspect','can_halt','can_refuse')):
                rt['state']='suspended'; rt['fence']+=1
                return result('escalate','R7','sponsor practical powers absent; suspended')
            if not self.capabilities.get(g['recovery']['capability_ref'],False): return result('escalate','R7','stop/recovery capability unavailable')
            if g['recovery']['attestation']['expires_at']<=self.now: return result('escalate','R7','recovery attestation expired')
            if e['reversibility'] not in g['recovery']['permitted_reversibility']: return result('deny','R7','reversibility outside accepted conditions')
        return result('allow',reason='R1–R7 satisfied',ledger_ids=sorted(ledger_ids),approval_id=e['approval_id'] if needed else None,chain=[g['identity']['grant_id'] for g in chain])

    def admit(self,e):
        with self.lock:
            self.attempts.append({'phase':'admit','time':self.now,'effect':deepcopy(e)})
            old=self.effects.get(e.get('effect_id'))
            if old:
                if old['effect']!=e: return result('deny','R4','effect ID reused with different payload')
                if old['status']=='committed': return result('allow',reason='idempotent receipt',status='committed')
                if old['status']!='admitted': return result('escalate','R1','terminal/unknown attempt requires reconciliation or new effect ID')
            r=self._check(e,old)
            if r['outcome']!='allow': return r
            if not old:
                # All-or-nothing in the process-local critical section. No failure
                # injection is supported inside these Python assignments.
                for lid in r['ledger_ids']: self.ledgers[lid]['reservations'][e['effect_id']]=e['units']
                if r['approval_id']: self.approvals[r['approval_id']]['claimed_by']=e['effect_id']
                self.effects[e['effect_id']]={'effect':deepcopy(e),'status':'admitted','ledgers':r['ledger_ids'],'fences':{g:self.runtime[g]['fence'] for g in r['chain']},'sponsor_at_admission':{g:self.sponsors[self.grants[g]['identity']['actor_id']]['human_id'] for g in r['chain']}}
                self.audit.append({'event':'intent_recorded','effect_id':e['effect_id'],'time':self.now,'payload_digest':digest(e),'rules':['R1','R2','R3','R4','R5','R6','R7']})
            return result('allow',reason='reserved and intent recorded',status='admitted')

    def _release(self,rec):
        for lid in rec['ledgers']: self.ledgers[lid]['reservations'].pop(rec['effect']['effect_id'],None)
        # Approval remains spent even when no effect committed; obtain a new one.

    def commit(self,effect_id,endpoint='success'):
        with self.lock:
            if endpoint not in ('success','known_failure','unknown'): raise ValueError('unknown endpoint simulation')
            if effect_id not in self.effects: return result('deny','R1','no admission')
            rec=self.effects[effect_id]; e=rec['effect']
            self.attempts.append({'phase':'commit','time':self.now,'effect_id':effect_id})
            if rec['status']=='committed': return result('allow',reason='idempotent receipt',status='committed')
            if rec['status']!='admitted': return result('escalate','R1','not committable without reconciliation')
            r=self._check(e,rec)
            if r['outcome']!='allow':
                rec['status']='canceled'; self._release(rec)
                self.audit.append({'event':'canceled_before_endpoint','effect_id':effect_id,'time':self.now,'rule':r['rule']})
                return r
            if endpoint=='unknown':
                rec['status']='unknown'; self.audit.append({'event':'unknown','effect_id':effect_id,'time':self.now})
                return result('escalate',reason='unknown outcome; reservation and approval retained',status='unknown')
            if endpoint=='known_failure':
                rec['status']='failed'; self._release(rec); self.failure_count+=1
                self.audit.append({'event':'failed','effect_id':effect_id,'time':self.now})
                return result('deny',reason='authoritative endpoint failure; no effect',status='failed')
            self._settle(rec)
            return result('allow',reason='simulated endpoint committed once',status='committed')

    def _settle(self,rec):
        e=rec['effect']; self._release(rec)
        for lid in rec['ledgers']: self.ledgers[lid]['committed']+=e['units']
        rec['status']='committed'; self.committed.append(deepcopy(e))
        rec['sponsor_at_commit']={g:self.sponsors[self.grants[g]['identity']['actor_id']]['human_id'] for g in rec['fences']}
        for gid in rec['fences']:
            rt=self.runtime[gid]; rt['commit_count']+=1; samp=self.grants[gid]['review_contract']['sampling']
            if samp['method']=='all' or rt['commit_count']%samp['every_n']==0: rt['pending_samples'].append(e['effect_id'])
        self.audit.append({'event':'committed','effect_id':e['effect_id'],'time':self.now,'units':e['units']})

    def reconcile_not_committed(self,effect_id):
        """Trusted endpoint confirmation only. Committed-but-unobserved is unmodeled."""
        with self.lock:
            rec=self.effects[effect_id]
            if rec['status']!='unknown': raise ValueError('not unknown')
            rec['status']='failed'; self._release(rec); self.failure_count+=1
            self.audit.append({'event':'reconciled_not_committed','effect_id':effect_id,'time':self.now})
            return result('allow',reason='reservation released; approval stays spent')

    def transfer_sponsor(self,actor_id,human_id,accepted,attestation):
        """Trusted registry transaction representing accepted human succession."""
        with self.lock:
            if not accepted or not attestation.get('evidence_ref') or attestation.get('expires_at',0)<=self.now:
                return result('escalate','R1','accepted successor evidence required')
            sp=self.sponsors[actor_id]
            sp.update(human_id=human_id,accepted=True,standing=True,present=True,acceptance_ref='synthetic:accepted-successor',independence_attestation=deepcopy(attestation))
            return result('allow',reason='accepted succession recorded; history preserved')

    def revoke(self,gid):
        with self.lock:
            self.runtime[gid]['state']='revoked'; self.runtime[gid]['fence']+=1
            return result('allow',reason='revocation fence advanced')

    def governance(self,gid,actor_type,operation):
        with self.lock:
            if actor_type!='human': return result('deny','R3','machine proposal does not change authority')
            if operation!='resume': return result('escalate','R3','new human-authorized immutable grant required')
            if self.runtime[gid]['state']!='suspended': return result('deny','R1','only suspended grants may resume')
            self.runtime[gid]['state']='active'; self.runtime[gid]['fence']+=1
            return result('allow',reason='trusted human resumption; prerequisites still rechecked')

    def review(self,gid,reviewer,sample_ids,aggregate_checks):
        with self.lock:
            g=self.grants[gid]; rt=self.runtime[gid]
            if reviewer not in g['review_contract']['reviewer_ids'] or not self.roles.get(reviewer): return result('deny','R6','unauthorized reviewer')
            if not set(rt['pending_samples'])<=set(sample_ids) or not set(g['review_contract']['aggregate_checks'])<=set(aggregate_checks): return result('escalate','R6','review evidence incomplete')
            self.review_log.append({'grant_id':gid,'reviewer':reviewer,'time':self.now,'examined_effect_ids':list(sample_ids),'aggregate_exposure':{k:v['committed']+sum(v['reservations'].values()) for k,v in self.ledgers.items()},'failure_count':self.failure_count,'checks':list(aggregate_checks)})
            rt['pending_samples']=[]; rt['review_due_at']=self.now+g['review_contract']['cadence_ticks']
            return result('allow',reason='review recorded; does not itself resume suspended authority')

    def snapshot(self):
        return {'time':self.now,'committed_effect_ids':[e['effect_id'] for e in self.committed],'ledgers':{k:{'committed':v['committed'],'reserved':sum(v['reservations'].values()),'limit':v['limit_units']} for k,v in sorted(self.ledgers.items())},'effect_states':{k:v['status'] for k,v in self.effects.items()},'grant_states':{k:v['state'] for k,v in self.runtime.items()},'approval_claims':{k:v['claimed_by'] for k,v in self.approvals.items()},'attempt_count':len(self.attempts),'audit_count':len(self.audit)}
