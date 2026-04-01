from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import time
import random

app = FastAPI()


with open("config.json") as f:
    CONFIG = json.load(f)


REQUEST_DB = {}
AUDIT_DB = {}


class RequestModel(BaseModel):
    request_id: str
    type: str
    data: dict


def evaluate_rule(rule, data):
    field = rule["field"]
    op = rule["operator"]
    value = rule["value"]
    actual = data.get(field)

    if actual is None:
        return "FAIL", f"{field} missing"

    if op == ">":
        result = actual > value
    elif op == "<":
        result = actual < value
    else:
        return "FAIL", "Unsupported operator"

    if result:
        reason = f"{field}={actual} satisfies {op} {value}"
    else:
        reason = f"{field}={actual} does NOT satisfy {op} {value}"

    return ("PASS" if result else "FAIL"), reason


def external_service(retries=2):
    for attempt in range(retries):
        try:
            if random.random() < 0.3:
                raise Exception("External dependency failure")
            return True
        except:
            if attempt == retries - 1:
                raise


def process_request(req: RequestModel):

   
    if req.request_id in REQUEST_DB:
        return REQUEST_DB[req.request_id]

    required_fields = ["income", "credit_score"]
    for field in required_fields:
        if field not in req.data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    workflow = CONFIG["workflows"].get(req.type)
    if not workflow:
        raise HTTPException(status_code=400, detail="Invalid workflow type")

    rules = workflow["rules"]

  
    state = {
        "status": "CREATED",
        "history": []
    }

    def update_state(new_status):
        state["status"] = new_status
        state["history"].append({
            "status": new_status,
            "timestamp": time.time()
        })

 
    audit = {
        "request_id": req.request_id,
        "input": req.data,
        "rules": [],
        "decision": None,
        "timestamp": time.time()
    }

    results = []

    try:
        update_state("VALIDATED")
        update_state("PROCESSING")

        all_pass = True

    
        for rule_name in rules:
            rule = CONFIG["rules"][rule_name]

            result, reason = evaluate_rule(rule, req.data)

            results.append({
                "rule": rule_name,
                "result": result,
                "reason": reason
            })

            if result == "FAIL":
                all_pass = False

        audit["rules"] = results

     
        if all_pass:
            external_service()
            decision = workflow["on_pass"]
        else:
            decision = workflow["on_fail"]

        update_state(decision)
        audit["decision"] = decision

    except Exception as e:
        update_state("RETRY")
        audit["decision"] = "RETRY"
        audit["error"] = str(e)

    
    audit["state_history"] = state["history"]

    REQUEST_DB[req.request_id] = state
    AUDIT_DB[req.request_id] = audit

    return state


@app.post("/request")
def create_request(req: RequestModel):
    return process_request(req)

@app.get("/request/{req_id}")
def get_status(req_id: str):
    return REQUEST_DB.get(req_id, "Not Found")

@app.post("/request/{req_id}/retry")
def retry(req_id: str):
    if req_id not in REQUEST_DB:
        raise HTTPException(status_code=404, detail="Not found")

    REQUEST_DB.pop(req_id)
    return {"message": "Retry triggered"}

@app.get("/audit/{req_id}")
def audit(req_id: str):
    return AUDIT_DB.get(req_id, "No audit found")
