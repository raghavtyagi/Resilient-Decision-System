from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_happy_path():
    res = client.post("/request", json={
        "request_id": "1",
        "type": "loan_application",
        "data": {"income": 50000, "credit_score": 700}
    })
    assert res.status_code == 200

def test_invalid_input():
    res = client.post("/request", json={
        "request_id": "2",
        "type": "loan_application",
        "data": {"income": 50000}
    })
    assert res.status_code == 400

def test_duplicate():
    payload = {
        "request_id": "3",
        "type": "loan_application",
        "data": {"income": 50000, "credit_score": 700}
    }
    client.post("/request", json=payload)
    res2 = client.post("/request", json=payload)
    assert res2.status_code == 200

def test_retry_flow():
    client.post("/request", json={
        "request_id": "4",
        "type": "loan_application",
        "data": {"income": 10000, "credit_score": 500}
    })
    res = client.post("/request/4/retry")
    assert res.status_code == 200
