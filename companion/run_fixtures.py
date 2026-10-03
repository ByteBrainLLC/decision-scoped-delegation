# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Replay checked-in fixtures; never generate expected outcomes from observations."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from monitor import Monitor, validate_grant
ROOT=Path(__file__).resolve().parent

def set_path(obj,path,value):
    parts=path.split('.')
    for part in parts[:-1]: obj=obj[part] if isinstance(obj,dict) else getattr(obj,part)
    if isinstance(obj,dict):obj[parts[-1]]=deepcopy(value)
    else:setattr(obj,parts[-1],deepcopy(value))
def patched(obj,changes):
    obj=deepcopy(obj)
    for k,v in changes.items():set_path(obj,k,v)
    return obj

def run_case(case,full_schema=False):
    g=patched(json.loads((ROOT/'fixtures/grant.json').read_text()),case['grant_patch'])
    validate_grant(g,full_schema); m=Monitor(g); effects={}; records=[]; failures=[]
    template=json.loads((ROOT/'fixtures/effect.json').read_text())
    for i,s in enumerate(case['steps']):
        op=s['op']; r=None
        if op=='effect': effects[s['id']]=patched(template,dict(s['patch'],effect_id=s['id'],decision_id='D-'+s['id']))
        elif op=='edit_effect': effects[s['id']]=patched(effects[s['id']],s['patch'])
        elif op=='state':set_path(m,s['path'],s['value'])
        elif op=='time':
            if s['value']<m.now:raise ValueError('time cannot reverse')
            m.now=s['value']
        elif op=='derive':
            child=patched(g,{'identity.grant_id':s['id'],'identity.actor_id':s['actor'],'identity.parent_grant_id':'G-root',**s.get('patch',{})})
            validate_grant(child,full_schema);r=m.derive(child)
        elif op=='approve':m.approve(effects[s['id']],approver=s.get('approver','human-issuer'),expires_at=s.get('expires_at',50),approval_id=s.get('approval_id','A1'))
        elif op=='admit':r=m.admit(effects[s['id']])
        elif op=='commit':r=m.commit(s['id'],s['endpoint'])
        elif op=='transfer':r=m.transfer_sponsor(s['actor'],s['human'],True,{'assessor_id':'human-assessor','evidence_ref':'synthetic:successor-attestation','expires_at':100})
        elif op=='revoke':r=m.revoke(s['id'])
        elif op=='governance':r=m.governance('G-root',s['actor_type'],s['operation'])
        elif op=='review':r=m.review(s['id'],'human-reviewer',s['sample_ids'],s['checks'])
        elif op=='reconcile':r=m.reconcile_not_committed(s['id'])
        else:raise ValueError('unsupported fixture op '+op)
        if r is not None:
            expected=s.get('expected',{})
            passed=all(r.get(k)==v for k,v in expected.items())
            records.append({'step':i+1,'operation':op,'expected':expected,'observed':r,'passed':passed,'state':m.snapshot()})
            if not passed: failures.append(f'step {i+1}: expected {expected}, got {r}')
    snap=m.snapshot()
    if snap['committed_effect_ids']!=case['expected_committed']:failures.append('committed effect oracle mismatch')
    if 'expected_ledger' in case and snap['ledgers']['L-shared']!=case['expected_ledger']:failures.append('ledger oracle mismatch')
    return {'id':case['id'],'category':case['category'],'passed':not failures,'failures':failures,'expected_committed':case['expected_committed'],'observed_committed':snap['committed_effect_ids'],'transitions':records,'final_state':snap,'audit':m.audit,'review_log':m.review_log,'note':case.get('note','')}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--full-schema',action='store_true');ap.add_argument('--output',default='results/fixture-results.json');args=ap.parse_args()
    cases=json.loads((ROOT/'fixtures/cases.json').read_text())['cases'];results=[run_case(c,args.full_schema) for c in cases]
    report={'artifact_version':'1.0.2','validation_mode':'jsonschema Draft202012Validator' if args.full_schema else 'custom model shape checks (not full JSON Schema validation)','scope':'deterministic synthetic process-local simulation; no real external effects or human study','cases':len(results),'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'asserted_transitions':sum(len(r['transitions']) for r in results),'results':results}
    p=ROOT/args.output;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n')
    trace=next(r for r in results if r['id']=='shared_children_a_first')
    (ROOT/'results/worked-trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    for r in results:
        if not r['passed']:print(r['id'],r['failures'],file=sys.stderr)
    return 1 if report['failed'] else 0
if __name__=='__main__':raise SystemExit(main())
