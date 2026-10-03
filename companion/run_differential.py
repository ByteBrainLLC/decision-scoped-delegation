# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Isolated differential: specified static controls versus a shared budget.

The static arm intentionally has NO cumulative admission/reservation ledger. It
uses a commit log solely for endpoint deduplication and post-hoc measurement. That
log's sum is never consulted when admitting a request. This is not a general
comparison of all possible static permission systems or production architectures.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
from monitor import Monitor, check_effect, digest, result, validate_grant
ROOT=Path(__file__).resolve().parent

class StaticPermissionsAndPerCall:
    """Fixed-context baseline implementing only the expressly listed controls."""
    def __init__(self,policy):
        self.policy=deepcopy(policy);self.admitted={};self.endpoint_receipts={}
        if policy['cumulative_control']!='none':raise ValueError('baseline must explicitly declare no cumulative control')

    def admit(self,e):
        check_effect(e);p=self.policy
        if p['allowed_actors_and_grants'].get(e['actor_id'])!=e['grant_id']:
            return result('deny','BASELINE_SCOPE','actor/grant outside static permissions')
        for field in ('grant_version','policy_version','configuration_version','decision_class'):
            if e[field]!=p[field]:return result('deny','BASELINE_SCOPE','fixed context or version mismatch')
        fields={'operation':'operations','resource':'resources','recipient':'recipients','data_class':'data_classes','environment':'environments','purpose':'purposes'}
        for field,allowed in fields.items():
            if e[field] not in p['permitted_effects'][allowed]:return result('deny','BASELINE_SCOPE','outside static '+field+' permission')
        if e['context']!=p['required_context'] or e['reversibility']!='restorable' or e['approval_id'] is not None:
            return result('deny','BASELINE_CONTEXT','outside the fixed differential context')
        if e['units']>p['per_effect_units']:return result('deny','BASELINE_PER_CALL','per-call limit exceeded')
        if e['effect_id'] in self.admitted and self.admitted[e['effect_id']]!=e:return result('deny','BASELINE_ID','different payload reused identifier')
        self.admitted[e['effect_id']]=deepcopy(e)
        return result('allow',reason='static permissions and per-call cap satisfied; no cumulative check')

    def commit(self,effect_id):
        if effect_id not in self.admitted:return result('deny','BASELINE_ID','no admission')
        self.endpoint_receipts.setdefault(effect_id,deepcopy(self.admitted[effect_id]))
        return result('allow',reason='simulated endpoint committed once',status='committed')


def run(full_schema=False):
    f=json.loads((ROOT/'fixtures/differential.json').read_text())
    # Confirm the differential changes only the declared aggregate-control
    # dimension, with identical scope, per-call cap, descriptors and fixed q.
    root=f['root_grant'];static_policy=f['policies']['static'];shared_policy=f['policies']['shared']
    validate_grant(root,full_schema)
    assert static_policy['permitted_effects']==root['permitted_effects']
    assert static_policy['per_effect_units']==shared_policy['per_effect_units']==root['exposure']['per_effect_units']==70
    assert root['exposure']['ledgers']==[{'ledger_id':'L-shared','limit_units':100,'aggregation_scope':'WF-research','epoch':'E1'}]
    assert shared_policy['shared_limit_units']==100
    assert [e['units'] for e in f['requests']]==[60,60]
    assert f['context']['time']==0
    static=StaticPermissionsAndPerCall(static_policy);shared=Monitor(root)
    for g in f['child_grants']:
        validate_grant(g,full_schema);assert shared.derive(g)['outcome']=='allow'
    arms={}
    for arm,engine in [('static',static),('shared',shared)]:
        inputs=deepcopy(f['requests']);transitions=[];admissions=[];accepted=[]
        for e in inputs:
            r=engine.admit(e)
            admissions.append({'effect_id':e['effect_id'],'outcome':r['outcome'],'rule':r['rule']})
            transitions.append({'phase':'admit','effect_id':e['effect_id'],'observed':r})
            if r['outcome']=='allow':accepted.append(e['effect_id'])
        for eid in accepted:
            r=engine.commit(eid);transitions.append({'phase':'commit','effect_id':eid,'observed':r})
        if arm=='static':
            committed=list(engine.endpoint_receipts.values())
            observed={'admissions':admissions,'committed_effect_ids':[e['effect_id'] for e in committed],'committed_units':sum(e['units'] for e in committed),'reservation_ledger_present':False}
        else:
            snap=engine.snapshot()
            observed={'admissions':admissions,'committed_effect_ids':snap['committed_effect_ids'],'committed_units':snap['ledgers']['L-shared']['committed'],'reservation_ledger_present':True,'final_reserved_units':snap['ledgers']['L-shared']['reserved']}
        expected=f['expected'][arm]
        arms[arm]={'input_sha256':digest(inputs),'expected':expected,'observed':observed,'passed':observed==expected,'transitions':transitions}
    same_inputs=arms['static']['input_sha256']==arms['shared']['input_sha256']
    return {'artifact_version':'1.0.2','experiment_id':f['experiment_id'],'validation_mode':'jsonschema Draft202012Validator' if full_schema else 'custom model shape checks (not full JSON Schema validation)','scope':f['scope'],'context':f['context'],'fixture_canonical_sha256':digest(f),'identical_request_inputs':same_inputs,'policy_arms':len(arms),'admission_observations':sum(t['phase']=='admit' for a in arms.values() for t in a['transitions']),'commit_observations':sum(t['phase']=='commit' for a in arms.values() for t in a['transitions']),'observed_transitions':sum(len(a['transitions']) for a in arms.values()),'passed':same_inputs and all(a['passed'] for a in arms.values()),'arms':arms,'interpretation':'Under these specified controls and fixed valid context, a per-call cap of 70 permits both 60-unit requests (120 committed); the shared 100-unit cap denies the second at R5 (60 committed). This does not show that all static-permission designs are unsafe.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--full-schema',action='store_true');ap.add_argument('--output',default='results/differential-results.json');args=ap.parse_args()
    report=run(args.full_schema);target=ROOT/args.output;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('arms','context')},indent=2))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
