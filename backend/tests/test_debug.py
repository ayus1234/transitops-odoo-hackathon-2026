import pytest
from fastapi.testclient import TestClient
import json

def test_debug(client: TestClient, admin_token_headers: dict):
    res = client.get("/api/v1/maintenance/scheduler", headers=admin_token_headers)
    print("STATUS:", res.status_code)
    print("BODY:", json.dumps(res.json(), indent=2))
    assert res.status_code == 200
