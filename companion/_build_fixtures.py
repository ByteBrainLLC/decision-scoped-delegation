# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Author predeclared scenario inputs/oracles. Never imports/runs the monitor."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent/'fixtures'
att={'assessor_id':'human-assessor','evidence_ref':'synthetic:assurance-v1','expires_at':100}
grant={
 'schema_version':'1.0.0',
 'identity':{'grant_id':'G-root','version':1,'policy_version':'P1','configuration_version':'C1','workflow_id':'WF-research','actor_id':'agent-root','parent_grant_id':None},
 'principal':{'id':'org-example'},'issuer':{'human_id':'human-issuer','authority_ref':'synthetic:role-delegator'},
 'sponsor':{'human_id':'human-sponsor','acceptance_ref':'synthetic:accepted-research','coverage_ref':'synthetic:coverage-plan','independence_attestation':att},
 'decision_scope':{'decision_class':'corpus-analysis','book_rung':3,'human_reserved_operations':['change_bounds']},
 'intent':{'version':'I1','outcome':'Produce an internal synthesis from the approved corpus','context':'Synthetic sandbox research; no real persons, accounts, or services','constraints':'Use the approved corpus only; no external transmission','tolerances':'At most 70 units per effect and 100 shared units in accounting epoch E1','the_line':'Do not widen corpus, recipients, purpose, or budget; ask the human issuer'},
 'pinned_predicates':{'language':'edf-exact-v1','version':'1','predicates':[{'field':'context.corpus_allowed','op':'eq','value':True}],'alignment_attestation':dict(att,status='aligned')},
 'permitted_effects':{'operations':['analyze'],'resources':['approved-corpus'],'recipients':['internal'],'data_classes':['synthetic'],'environments':['sandbox'],'purposes':['research-synthesis']},
 'exposure':{'per_effect_units':70,'ledgers':[{'ledger_id':'L-shared','limit_units':100,'aggregation_scope':'WF-research','epoch':'E1'}]},
 'approvals':{'required':False,'approver_ids':['human-issuer','human-reviewer'],'separation_from_issuer':False},
 'review_contract':{'reviewer_ids':['human-reviewer'],'decision_timing':'within_bounds','cadence_ticks':20,'sampling':{'method':'all','every_n':1},'aggregate_checks':['exposure_total','failure_count'],'lapse_action':'suspend','evidence_required':True},
 'recovery':{'permitted_reversibility':['restorable','irreversible'],'requires_human_key_for_irreversible':True,'capability_ref':'synthetic:stop-and-restore','attestation':att},
 'lifecycle':{'not_before':0,'expires_at':100,'initial_state':'active','resume_requires_human':True},
 'derivation':{'allowed_actor_ids':['child-a','child-b'],'allowed_sponsor_ids':['human-sponsor'],'max_depth':2}
}
effect={'effect_id':'E1','decision_id':'D1','actor_id':'agent-root','grant_id':'G-root','grant_version':1,'policy_version':'P1','configuration_version':'C1','decision_class':'corpus-analysis','purpose':'research-synthesis','operation':'analyze','resource':'approved-corpus','recipient':'internal','data_class':'synthetic','environment':'sandbox','units':40,'payload':{'query':'Summarize licensing terms'},'context':{'corpus_allowed':True},'reversibility':'restorable','approval_id':None}

def step(op,expected=None,**kw):
 d={'op':op,**kw}
 if expected is not None:d['expected']=expected
 return d
def expect(outcome,rule=None): return {'outcome':outcome,'rule':rule}
def add(e='E1',**patch): return step('effect',id=e,patch=patch)
def admit(e='E1',out='allow',rule=None): return step('admit',expect(out,rule),id=e)
def commit(e='E1',out='allow',rule=None,endpoint='success'):return step('commit',expect(out,rule),id=e,endpoint=endpoint)
def patch(path,value):return step('state',path=path,value=value)
def case(id,category,steps,committed,grant_patch=None,ledger=None,**extra):
 c={'id':id,'category':category,'grant_patch':grant_patch or {},'steps':steps,'expected_committed':committed,**extra}
 if ledger is not None:c['expected_ledger']=ledger
 return c
r2={'decision_scope.book_rung':2,'review_contract.decision_timing':'before_commit'}
ap=lambda e='E1',**kw:step('approve',id=e,**kw)
child=lambda id='G-a',actor='child-a',**kw:step('derive',expect('allow'),id=id,actor=actor,patch=kw)
cs=[]
cs.append(case('positive_bounded_commit','baseline',[add(),admit(),commit(),commit()],['E1'],ledger={'committed':40,'reserved':0,'limit':100}))
cs.append(case('positive_exact_human_choice','approval_drift',[add(approval_id='A1'),ap(),admit(),commit()],['E1'],r2))
cs.append(case('recommendation_waits_for_human','approval_drift',[add(),admit(out='escalate',rule='R4')],[],r2))
cs.append(case('modified_approved_payload','approval_drift',[add(approval_id='A1'),ap(),step('edit_effect',id='E1',patch={'payload.query':'Different consequential text'}),admit(out='escalate',rule='R4')],[],r2))
cs.append(case('stale_policy_approval','approval_drift',[add(approval_id='A1'),ap(),patch('runtime.G-root.policy_version','P2'),step('edit_effect',id='E1',patch={'policy_version':'P2'}),admit(out='escalate',rule='R4')],[],r2))
cs.append(case('expired_approval','approval_drift',[add(approval_id='A1'),ap(expires_at=5),step('time',value=5),admit(out='escalate',rule='R4')],[],r2))
cs.append(case('approval_cannot_authorize_second_effect','approval_drift',[add(approval_id='A1'),ap(),admit(),commit(),add('E2',approval_id='A1'),admit('E2','escalate','R4')],['E1'],r2))
cs.append(case('same_id_changed_payload','approval_drift',[add(),admit(),step('edit_effect',id='E1',patch={'payload.query':'Changed after admission'}),admit(out='deny',rule='R4'),commit()],['E1']))
cs.append(case('separation_of_duties','approval_drift',[add(approval_id='A1'),ap(),admit(out='deny',rule='R4')],[],dict(r2,**{'approvals.separation_from_issuer':True})))
cs.append(case('many_small_aggregate_exceeds','scope_and_exposure',[add(),admit(),commit(),add('E2'),admit('E2'),commit('E2'),add('E3',units=30),admit('E3','deny','R5')],['E1','E2'],ledger={'committed':80,'reserved':0,'limit':100}))
for first,second in [('a','b'),('b','a')]:
 cs.append(case('shared_children_'+first+'_first','scope_and_exposure',[child(),child('G-b','child-b'),add('E-a',actor_id='child-a',grant_id='G-a',units=60),add('E-b',actor_id='child-b',grant_id='G-b',units=60),admit('E-'+first),admit('E-'+second,'deny','R5'),commit('E-'+first)],['E-'+first],ledger={'committed':60,'reserved':0,'limit':100}))
cs.append(case('child_ambient_permission_does_not_widen','scope_and_exposure',[child(**{'permitted_effects.operations':['analyze','upload'],'permitted_effects.recipients':['internal','outside']}),add(actor_id='child-a',grant_id='G-a',operation='upload',recipient='outside'),admit(out='deny',rule='R2')],[]))
cs.append(case('positive_child_attenuation','scope_and_exposure',[child(),add(actor_id='child-a',grant_id='G-a'),admit(),commit()],['E1']))
cs.append(case('orphaned_queued_actor','sponsor_and_cessation',[add(),admit(),patch('sponsors.agent-root.accepted',False),commit(out='deny',rule='R1')],[],ledger={'committed':0,'reserved':0,'limit':100}))
cs.append(case('positive_absence_with_accepted_coverage','sponsor_and_cessation',[patch('sponsors.agent-root.present',False),patch('sponsors.agent-root.coverage_valid',True),add(),admit(),commit()],['E1']))
cs.append(case('absence_without_coverage','sponsor_and_cessation',[patch('sponsors.agent-root.present',False),add(),admit(out='deny',rule='R1')],[]))
cs.append(case('sponsor_cannot_halt','sponsor_and_cessation',[patch('sponsors.agent-root.can_halt',False),add(),admit(out='escalate',rule='R7')],[]))
cs.append(case('accepted_sponsor_successor','sponsor_and_cessation',[add(),admit(),step('transfer',expect('allow'),actor='agent-root',human='human-successor'),commit()],['E1'],note='Trusted registry input represents accepted transfer; no authentication or institutional validation implemented.'))
for rung in [3,4]:
 cs.append(case('rung_'+str(rung)+'_review_lapse','review_and_intent',[add(),admit(),step('time',value=20),commit(out='escalate',rule='R6')],[],{'decision_scope.book_rung':rung,'review_contract.decision_timing':{3:'within_bounds',4:'retrospective'}[rung]}))
cs.append(case('positive_review_cycle','review_and_intent',[add(),admit(),commit(),step('time',value=19),step('review',expect('allow'),id='G-root',sample_ids=['E1'],checks=['exposure_total','failure_count']),step('time',value=21),add('E2'),admit('E2'),commit('E2')],['E1','E2']))
cs.append(case('incomplete_review_does_not_refresh','review_and_intent',[add(),admit(),commit(),step('time',value=19),step('review',expect('escalate','R6'),id='G-root',sample_ids=[],checks=['exposure_total','failure_count']),step('time',value=20),add('E2'),admit('E2','escalate','R6')],['E1']))
cs.append(case('review_resume_requires_human','review_and_intent',[step('time',value=20),add(),admit(out='escalate',rule='R6'),step('review',expect('allow'),id='G-root',sample_ids=[],checks=['exposure_total','failure_count']),step('governance',expect('deny','R3'),actor_type='machine',operation='resume'),step('governance',expect('allow'),actor_type='human',operation='resume'),admit(),commit()],['E1']))
cs.append(case('intent_predicate_known_mismatch','review_and_intent',[add(),admit(out='escalate',rule='R2')],[],{'pinned_predicates.alignment_attestation.status':'mismatch'}))
cs.append(case('mandatory_predicate_unknown','review_and_intent',[add(context={}),admit(out='escalate',rule='R2')],[]))
cs.append(case('pinned_predicate_false','review_and_intent',[add(context={'corpus_allowed':False}),admit(out='deny',rule='R2')],[]))
cs.append(case('intent_text_alone_is_not_enforced','review_and_intent',[add(),admit(),commit()],['E1'],{'intent.constraints':'Never analyze any corpus'},note='Intentional limitation: falsely marked aligned attestation lets inconsistent prose pass. Model cannot understand or prove prose/predicate equivalence. This is a positive admission counterexample to any stronger assurance claim.'))
cs.append(case('adaptation_does_not_promote_authority','human_bounds',[step('governance',expect('deny','R3'),actor_type='machine',operation='expand')],[]))
cs.append(case('governing_effect_remains_human','human_bounds',[add(operation='change_bounds'),admit(out='deny',rule='R3')],[],{'permitted_effects.operations':['analyze','change_bounds']}))
cs.append(case('revoked_ancestor_blocks_queued_commit','sponsor_and_cessation',[child(),add(actor_id='child-a',grant_id='G-a'),admit(),step('revoke',expect('allow'),id='G-root'),commit(out='deny',rule='R1')],[],ledger={'committed':0,'reserved':0,'limit':100}))
cs.append(case('expiry_at_commit','sponsor_and_cessation',[add(),admit(),step('time',value=100),commit(out='deny',rule='R1')],[]))
cs.append(case('unknown_outcome_retains_exposure','failure_handling',[add(approval_id='A1'),ap(),admit(),commit(out='escalate',endpoint='unknown'),commit(out='escalate',rule='R1'),add('E2',units=70,approval_id='A2'),ap('E2',approval_id='A2'),admit('E2','deny','R5')],[],r2,ledger={'committed':0,'reserved':40,'limit':100}))
cs.append(case('reconciliation_releases_only_known_unused','failure_handling',[add(approval_id='A1'),ap(),admit(),commit(out='escalate',endpoint='unknown'),step('reconcile',expect('allow'),id='E1')],[],r2,ledger={'committed':0,'reserved':0,'limit':100}))
cs.append(case('known_failure_releases_reservation','failure_handling',[add(approval_id='A1'),ap(),admit(),commit(out='deny',endpoint='known_failure')],[],r2,ledger={'committed':0,'reserved':0,'limit':100}))
cs.append(case('audit_unavailable_fails_closed','failure_handling',[patch('audit_available',False),add(),admit(out='escalate',rule='R6')],[],ledger={'committed':0,'reserved':0,'limit':100}))
cs.append(case('recovery_unavailable_fails_closed','failure_handling',[patch('capabilities.synthetic:stop-and-restore',False),add(),admit(out='escalate',rule='R7')],[]))
cs.append(case('per_effect_cap','scope_and_exposure',[add(units=71),admit(out='deny',rule='R5')],[]))
cs.append(case('negative_exposure_rejected','scope_and_exposure',[add(units=-1),admit(out='deny',rule='R1')],[]))
cs.append(case('irreversible_requires_human_key','approval_drift',[add(reversibility='irreversible'),admit(out='escalate',rule='R4')],[]))
cs.append(case('positive_irreversible_exact_human_key','approval_drift',[add(reversibility='irreversible',approval_id='A1'),ap(),admit(),commit()],['E1']))
cs.append(case('new_epoch_does_not_reset_shared_ledger','scope_and_exposure',[step('derive',expect('deny','R1'),id='G-a',actor='child-a',patch={'exposure.ledgers':[{'ledger_id':'L-shared','limit_units':100,'aggregation_scope':'WF-research','epoch':'E2'}]})],[]))
cs.append(case('lower_cap_below_spend_stops_new_work','scope_and_exposure',[add(units=60),admit(),commit(),patch('ledgers.L-shared.limit_units',50),add('E2',units=1),admit('E2','deny','R5')],['E1'],ledger={'committed':60,'reserved':0,'limit':50},note='Trusted human cap contraction records existing overage; no claim that historical exposure met the new cap.'))
cs.append(case('rung4_irreversible_requires_new_exact_contract','human_bounds',[add(reversibility='irreversible',approval_id='A1'),ap(),admit(out='escalate',rule='R3')],[],{'decision_scope.book_rung':4,'review_contract.decision_timing':'retrospective'}))
for name,data in [('grant.json',grant),('effect.json',effect),('cases.json',{'fixture_version':'1.0.0','oracle_type':'predeclared synthetic expected outcomes','cases':cs})]:
 (P/name).write_text(json.dumps(data,indent=2)+'\n')
print(len(cs),'predeclared cases')
