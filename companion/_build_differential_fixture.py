# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Write the pinned differential inputs and manually specified oracles.

Does not import or execute either policy implementation.
"""
from copy import deepcopy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
root=json.loads((ROOT/'fixtures/grant.json').read_text())
template=json.loads((ROOT/'fixtures/effect.json').read_text())
children=[];effects=[]
for suffix in ('a','b'):
    g=deepcopy(root);g['identity'].update(grant_id='G-'+suffix,actor_id='child-'+suffix,parent_grant_id='G-root');children.append(g)
    e=deepcopy(template);e.update(effect_id='E-'+suffix,decision_id='D-E-'+suffix,actor_id='child-'+suffix,grant_id='G-'+suffix,units=60);effects.append(e)
fixture={
 'fixture_version':'1.0.0',
 'experiment_id':'two_requests_static_vs_shared',
 'scope':'Synthetic budget-control differential only; same complete requests and fixed valid context in both arms',
 'context':{'time':0,'ordering':'admit both in a,b order; then commit each admitted effect in that order','human_and_scope_prerequisites':'trusted, valid and unchanged','endpoint':'in-process successful simulation'},
 'root_grant':root,'child_grants':children,'requests':effects,
 'policies':{
   'static':{'name':'static permissions plus per-call cap only','allowed_actors_and_grants':{'child-a':'G-a','child-b':'G-b'},'grant_version':1,'policy_version':'P1','configuration_version':'C1','decision_class':'corpus-analysis','permitted_effects':deepcopy(root['permitted_effects']),'required_context':{'corpus_allowed':True},'per_effect_units':70,'cumulative_control':'none'},
   'shared':{'name':'same permitted effects and per-call cap, with shared workflow ledger','per_effect_units':70,'shared_ledger_id':'L-shared','shared_limit_units':100,'aggregation_scope':'WF-research','epoch':'E1'}
 },
 'expected':{
   'static':{'admissions':[{'effect_id':'E-a','outcome':'allow','rule':None},{'effect_id':'E-b','outcome':'allow','rule':None}],'committed_effect_ids':['E-a','E-b'],'committed_units':120,'reservation_ledger_present':False},
   'shared':{'admissions':[{'effect_id':'E-a','outcome':'allow','rule':None},{'effect_id':'E-b','outcome':'deny','rule':'R5'}],'committed_effect_ids':['E-a'],'committed_units':60,'reservation_ledger_present':True,'final_reserved_units':0}
 }
}
(ROOT/'fixtures/differential.json').write_text(json.dumps(fixture,indent=2)+'\n')
