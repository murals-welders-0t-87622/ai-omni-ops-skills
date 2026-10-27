"""Check that a learning record has enough evidence and a user choice before execution.
This does not establish causality, verify identity, grant permission or write records.
"""
import json, sys
from datetime import datetime
from pathlib import Path

DECISIONS = {"pending-user-choice", "selected", "rejected", "cancelled"}
EXECUTIONS = {"not-started", "in-progress", "completed", "cancelled"}
RESULTS = {"not-observed", "support", "no-detectable-effect", "negative", "inconclusive"}

def validate(rec):
    errors=[]
    scope=rec.get("scope") or {};trigger=rec.get("trigger") or {};hyp=rec.get("hypothesis") or {}
    proposal=rec.get("proposal") or {};decision=rec.get("decision") or {};execution=rec.get("execution") or {};result=rec.get("result") or {}
    if not rec.get("id"): errors.append("missing stable record id")
    if not scope.get("brand") or not scope.get("object"): errors.append("missing brand/object")
    if trigger.get("kind") not in {"user-feedback","business-data","execution-feedback"}: errors.append("missing trigger kind")
    if not trigger.get("observation") or not trigger.get("sources"): errors.append("missing observed feedback and source")
    if not hyp.get("factor") or not hyp.get("mechanism") or not hyp.get("competingExplanations"): errors.append("missing hypothesis or competing explanation")
    if not proposal.get("action") or not proposal.get("testDesign") or not proposal.get("primaryMetric"): errors.append("missing actionable validation proposal")
    ds=decision.get("status"); es=execution.get("status"); rs=result.get("status")
    if ds not in DECISIONS: errors.append("invalid decision state")
    if es not in EXECUTIONS: errors.append("invalid execution state")
    if rs not in RESULTS: errors.append("invalid result state")
    if ds=="selected":
        if not decision.get("selectedBy") or not decision.get("selectedAt"): errors.append("user selection evidence missing")
        else:
            try: datetime.fromisoformat(decision["selectedAt"].replace("Z","+00:00"))
            except (ValueError,TypeError): errors.append("invalid selection timestamp")
    if es in {"in-progress","completed"} and ds!="selected": errors.append("execution requires user's selection")
    if rs!="not-observed":
        if ds!="selected" or es!="completed" or not execution.get("receipts"): errors.append("result requires selected and evidenced completed action")
        if not result.get("metrics") or not result.get("limitations"): errors.append("result requires observation and limitations")
        if rs=="no-detectable-effect" and not result.get("samples"): errors.append("absence of detectable effect requires sample/precision evidence")
    return errors

def main():
    if len(sys.argv)!=2: print("usage: validate_record.py record.json",file=sys.stderr);return 2
    try: errors=validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    except (ValueError,OSError) as e: print(str(e),file=sys.stderr);return 2
    print(json.dumps({"valid":not errors,"errors":errors},ensure_ascii=False));return bool(errors)
if __name__=="__main__":raise SystemExit(main())
