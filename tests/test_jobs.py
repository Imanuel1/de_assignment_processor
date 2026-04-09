
import asyncio
from datetime import datetime, timedelta
import time
import pytest



#Job submission and retrieval
@pytest.mark.asyncio
async def test_job_submission_and_retrieval(client):
    idempotency_key = f"test_submission_{int(time.time())}"
    payload = {
        "job_type": "email",
        "payload": {"to": "me", "subject": "test", "body": "hi friend"},
        "idempotency_key": idempotency_key,
        "priority": 1
    }
    response = await client.post("/jobs", json=payload)
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}, response: {response.text}"

    await asyncio.sleep(1)
    response = await client.get(f"/jobs/{idempotency_key}")
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, response: {response.text}"


#Job completion flow
@pytest.mark.asyncio
async def test_job_completion_flow(client):
    idempotency_key = f"test_complete_flow_{int(time.time())}"
    payload = {
        "job_type": "email",
        "payload": {"to": "me", "subject": "test", "body": "hi friend"},
        "idempotency_key": idempotency_key,
        "priority": 1
    }
    response = await client.post("/jobs", json=payload)
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}, response: {response.text}"


    completed = False
    for _ in range(10):
        await asyncio.sleep(1)
        response = await client.get(f"/jobs/{idempotency_key}")
        job = response.json()
        if job["status"] == "completed":
            completed = True
            break
    
    assert completed is True, "Job was never completed by worker"

#Job failure and retry
@pytest.mark.asyncio
async def test_job_failure_retry(client, monkeypatch):
    idempotency_key = f"retry_test_{int(time.time())}"

    await client.post("/jobs", json={
        "job_type": "webhook",
        "idempotency_key": idempotency_key,
        "payload": {"url": "http://test.com"}
    })


    for _ in range(10):
        await asyncio.sleep(0.5)
        res = await client.get(f"/jobs/{idempotency_key}")
        if res.json().get("status") == "failed":
            break
            
    assert res.json()["status"] == "failed", f"Expected job id {idempotency_key} to be failed after retries, got: {res.json()}"
    assert "Webhook call failed" in res.json().get("error", "")

#Cancellation
@pytest.mark.asyncio
async def test_job_cancellation(client):
    idempotency_key = f"test_cancel_{int(time.time())}"
    payload = {
        "job_type": "report", 
        "idempotency_key": idempotency_key,
        "scheduled_time": (datetime.now() + timedelta(days=2)).isoformat(),
        "payload": {
            "report_type": "important",
            "user_id": 35635635
        },
        "priority": 3
    }
    await client.post("/jobs", json=payload)
    
    res = await client.post(f"/jobs/{idempotency_key}/cancel")
    assert res.status_code == 200, f"Unexpected status code: {res.status_code}, idempotency_key: {idempotency_key}, response: {res.text}"

    res = await client.get(f"/jobs/{idempotency_key}")
    job = res.json()
    assert job["status"] == "canceled"

#Idempotency
@pytest.mark.asyncio
async def test_idempotency(client):
    idempotency_key = f"test_idempotency_{int(time.time())}"
    payload = {
        "job_type": "email", 
        "idempotency_key": idempotency_key, 
        "payload": {
            "to": "aba",
            "subject": "test",
            "body": "fffdg r tgtgtg"
        },
        "priority": 2
    }
    
    res1 = await client.post("/jobs", json=payload)
    res2 = await client.post("/jobs", json=payload)

    assert res1.status_code == 201
    assert res2.status_code == 200 # Should return OK - existing
    assert res2.json()["message"] == "Job already exists"


#Priority ordering
@pytest.mark.asyncio
async def test_priority_ordering(client):
    idedempotency_key_high = f"test_priority_high_{int(time.time())}"
    idedempotency_key_mid_1 = f"test_priority_mid_{int(time.time())}"
    idedempotency_key_mid_2 = f"test_priority_mid_{int(time.time())}"
    idedempotency_key_low = f"test_priority_low_{int(time.time())}"
    base_payload = {
        "job_type": "email", 
        "payload": {
            "to": "aba",
            "subject": "test",
            "body": "fffdg r tgtgtg"
        },
        "scheduled_time": (datetime.now() + timedelta(seconds=2)).isoformat()
    }
    await client.post("/jobs", json={**base_payload, "idempotency_key": idedempotency_key_high, "priority": 3})
    await client.post("/jobs", json={**base_payload, "idempotency_key": idedempotency_key_mid_1, "priority": 2})
    await client.post("/jobs", json={**base_payload, "idempotency_key": idedempotency_key_mid_2, "priority": 2})
    await client.post("/jobs", json={**base_payload, "idempotency_key": idedempotency_key_low, "priority": 1})

    await asyncio.sleep(3)

    res_high_priority = await client.get(f"/jobs/{idedempotency_key_high}")
    res_low_priority = await client.get(f"/jobs/{idedempotency_key_low}")
    job_high = res_high_priority.json()
    job_low = res_low_priority.json()
    start_low = datetime.fromisoformat(job_low["started_at"])
    start_high = datetime.fromisoformat(job_high["started_at"])

    assert start_high < start_low, f"Priority failed: High ({start_high}) started after Low ({start_low})"