# Copyright 2026 Ed Fassio and ByteBrain LLC
# SPDX-License-Identifier: Apache-2.0
# Version 1.0.2: licensing/citation metadata updated; decision semantics unchanged.

"""Maintainer utility: regenerate the published, self-contained schema."""
import json
from pathlib import Path
S={"type":"string","minLength":1}; I={"type":"integer","minimum":0}; B={"type":"boolean"}
def enum(*xs): return {"enum":list(xs)}
def arr(item=S, minimum=1): return {"type":"array","items":item,"minItems":minimum,"uniqueItems":True}
def obj(**props): return {"type":"object","properties":props,"required":list(props),"additionalProperties":False}
att=obj(assessor_id=S,evidence_ref=S,expires_at=I)
schema=obj(
 schema_version={"const":"1.0.0"},
 identity=obj(grant_id=S,version={"type":"integer","minimum":1},policy_version=S,configuration_version=S,workflow_id=S,actor_id=S,parent_grant_id={"type":["string","null"]}),
 principal=obj(id=S),issuer=obj(human_id=S,authority_ref=S),
 sponsor=obj(human_id=S,acceptance_ref=S,coverage_ref=S,independence_attestation=att),
 decision_scope=obj(decision_class=S,book_rung=enum(1,2,3,4),human_reserved_operations=arr()),
 intent=obj(version=S,outcome=S,context=S,constraints=S,tolerances=S,the_line=S),
 pinned_predicates=obj(language={"const":"edf-exact-v1"},version={"const":"1"},predicates=arr(obj(field=S,op=enum("eq","in","lte"),value={"type":["string","number","boolean","array"]}),0),alignment_attestation=obj(assessor_id=S,evidence_ref=S,expires_at=I,status=enum("aligned","mismatch","unknown"))),
 permitted_effects=obj(operations=arr(),resources=arr(),recipients=arr(),data_classes=arr(),environments=arr(),purposes=arr()),
 exposure=obj(per_effect_units=I,ledgers=arr(obj(ledger_id=S,limit_units=I,aggregation_scope=S,epoch=S))),
 approvals=obj(required=B,approver_ids=arr(),separation_from_issuer=B),
 review_contract=obj(reviewer_ids=arr(),decision_timing=enum("before_commit","within_bounds","retrospective"),cadence_ticks={"type":"integer","minimum":1},sampling=obj(method=enum("all","every_nth"),every_n={"type":"integer","minimum":1}),aggregate_checks=arr(enum("exposure_total","failure_count")),lapse_action={"const":"suspend"},evidence_required={"const":True}),
 recovery=obj(permitted_reversibility=arr(enum("restorable","compensable","irreversible")),requires_human_key_for_irreversible={"const":True},capability_ref=S,attestation=att),
 lifecycle=obj(not_before=I,expires_at=I,initial_state=enum("proposed","active"),resume_requires_human={"const":True}),
 derivation=obj(allowed_actor_ids=arr(S,0),allowed_sponsor_ids=arr(S,0),max_depth={"type":"integer","minimum":0,"maximum":8})
)
schema.update({"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"urn:edf:delegation-grant:1.0.0","title":"Synthetic delegation grant 1.0.0","description":"Proposed technical extension, not a schema reproduced from the book. Shape validation is not authorization."})
Path(__file__).with_name('grant.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
