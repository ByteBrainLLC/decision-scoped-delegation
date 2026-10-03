# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Focused edge tests supplement the separate predeclared scenario oracles."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest
from monitor import Monitor, validate_grant
from run_fixtures import patched, run_case
ROOT=Path(__file__).resolve().parents[1]

def load(name):return json.loads((ROOT/'fixtures'/name).read_text())

class MonitorTests(unittest.TestCase):
    def setUp(self):self.g=load('grant.json');self.e=load('effect.json');self.m=Monitor(self.g)
    def test_all_predeclared_fixtures(self):
        for case in load('cases.json')['cases']:
            with self.subTest(case=case['id']):self.assertTrue(run_case(case)['passed'])
    def test_schema_rejects_machine_rung_five(self):
        self.g['decision_scope']['book_rung']=5
        with self.assertRaises(ValueError):validate_grant(self.g)
    def test_schema_rejects_absent_intent_field(self):
        del self.g['intent']['the_line']
        with self.assertRaises(ValueError):validate_grant(self.g)
    def test_schema_rejects_missing_lapse_rule(self):
        del self.g['review_contract']['lapse_action']
        with self.assertRaises(ValueError):validate_grant(self.g)
    def test_schema_rejects_negative_limit(self):
        self.g['exposure']['per_effect_units']=-1
        with self.assertRaises(ValueError):validate_grant(self.g)
    def test_schema_rejects_ambiguous_boolean_cost(self):
        self.e['units']=True
        self.assertEqual(self.m.admit(self.e)['outcome'],'deny')
    def test_schema_rejects_unknown_predicate_operator(self):
        self.g['pinned_predicates']['predicates'][0]['op']='execute_python'
        with self.assertRaises(ValueError):validate_grant(self.g)
    def test_model_rejects_duplicate_ledger_ids(self):
        self.g['exposure']['ledgers'].append(dict(self.g['exposure']['ledgers'][0],limit_units=50))
        with self.assertRaises(ValueError):validate_grant(self.g)
    def test_grant_copied_at_install(self):
        self.g['permitted_effects']['operations'].append('upload')
        self.assertNotIn('upload',self.m.grants['G-root']['permitted_effects']['operations'])
    def test_post_install_grant_tamper_detected(self):
        self.m.grants['G-root']['exposure']['per_effect_units']=999
        self.assertEqual(self.m.admit(self.e)['rule'],'R1')
    def test_scope_failure_claims_nothing(self):
        self.e['recipient']='outside';self.m.admit(self.e)
        self.assertEqual(self.m.snapshot()['ledgers']['L-shared']['reserved'],0)
        self.assertEqual(self.m.audit,[])
    def test_commit_without_admission_rejected(self):self.assertEqual(self.m.commit('missing')['outcome'],'deny')
    def test_idempotent_commit_charged_once(self):
        self.m.admit(self.e);self.m.commit('E1');self.m.commit('E1')
        self.assertEqual(len(self.m.committed),1)
        self.assertEqual(self.m.ledgers['L-shared']['committed'],40)
    def test_failed_endpoint_does_not_refund_approval(self):
        m=Monitor(patched(self.g,{'approvals.required':True}));self.e['approval_id']='A1';m.approve(self.e);m.admit(self.e);m.commit('E1','known_failure')
        self.assertEqual(m.approvals['A1']['claimed_by'],'E1')
        self.assertEqual(m.snapshot()['ledgers']['L-shared']['reserved'],0)
    def test_unknown_endpoint_retains_approval_and_reservation(self):
        m=Monitor(patched(self.g,{'approvals.required':True}));self.e['approval_id']='A1';m.approve(self.e);m.admit(self.e);m.commit('E1','unknown')
        self.assertEqual(m.approvals['A1']['claimed_by'],'E1')
        self.assertEqual(m.snapshot()['ledgers']['L-shared']['reserved'],40)
    def test_approval_id_cannot_be_overwritten(self):
        self.m.approve(self.e)
        with self.assertRaises(ValueError):self.m.approve(self.e)
    def test_fence_blocks_revoked_then_reactivated_queue(self):
        self.m.admit(self.e);self.m.revoke('G-root');self.m.runtime['G-root']['state']='active'
        self.assertEqual(self.m.commit('E1')['reason'],'stale commit fence')
    def test_unaccepted_succession_not_installed(self):
        r=self.m.transfer_sponsor('agent-root','new',False,{})
        self.assertEqual(r['outcome'],'escalate');self.assertEqual(self.m.sponsors['agent-root']['human_id'],'human-sponsor')
    def test_sponsor_history_preserved_on_accepted_transfer(self):
        self.m.admit(self.e);self.m.transfer_sponsor('agent-root','new',True,{'assessor_id':'h','evidence_ref':'e','expires_at':100});self.m.commit('E1')
        r=self.m.effects['E1'];self.assertEqual(r['sponsor_at_admission']['G-root'],'human-sponsor');self.assertEqual(r['sponsor_at_commit']['G-root'],'new')
    def test_every_nth_sampling_and_aggregates(self):
        m=Monitor(patched(self.g,{'review_contract.sampling.method':'every_nth','review_contract.sampling.every_n':2}))
        for eid in ['E1','E2']:
            e=dict(self.e,effect_id=eid);m.admit(e);m.commit(eid)
        self.assertEqual(m.runtime['G-root']['pending_samples'],['E2'])
        self.assertEqual(m.review('G-root','human-reviewer',['E2'],['exposure_total'])['outcome'],'escalate')
        self.assertEqual(m.review('G-root','human-reviewer',['E2'],['exposure_total','failure_count'])['outcome'],'allow')
        self.assertEqual(m.review_log[-1]['aggregate_exposure']['L-shared'],80)
    def test_all_six_three_request_serial_orders(self):
        # Exhaustive arrival permutations for this tiny serialized case, NOT
        # distributed concurrency, scheduling, or multithreaded model checking.
        for order in itertools.permutations(['E1','E2','E3']):
            m=Monitor(self.g);outcomes=[]
            for eid in order:outcomes.append(m.admit(dict(self.e,effect_id=eid,units=60))['outcome'])
            self.assertEqual(outcomes,['allow','deny','deny'])
            self.assertEqual(m.snapshot()['ledgers']['L-shared']['reserved'],60)
    def test_child_ledger_conflict_is_atomic(self):
        c=patched(self.g,{'identity.grant_id':'G-a','identity.actor_id':'child-a','identity.parent_grant_id':'G-root','exposure.ledgers':[dict(self.g['exposure']['ledgers'][0],limit_units=999)]})
        self.assertEqual(self.m.derive(c)['outcome'],'deny');self.assertNotIn('G-a',self.m.grants)
    def test_bad_cap_contraction_retains_recorded_overage(self):
        self.m.admit(self.e);self.m.commit('E1');self.m.ledgers['L-shared']['limit_units']=20
        self.assertEqual(self.m.ledgers['L-shared']['committed'],40)
        self.assertEqual(self.m.admit(dict(self.e,effect_id='E2',units=1))['rule'],'R5')

if __name__=='__main__':unittest.main()
