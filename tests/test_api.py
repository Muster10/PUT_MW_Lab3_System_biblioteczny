from unittest.mock import patch
import pytest
from main import app

def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_health_db_error(client):
    with patch("main.polacz_z_db", side_effect=Exception("DB down")):
        res = client.get("/health")
    assert res.status_code == 503