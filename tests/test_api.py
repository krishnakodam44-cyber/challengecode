from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_search_dataset():
    # create a dataset
    payload = {
        "fqn": "test_conn.test_db.test_schema.test_table",
        "description": "test dataset",
        "source_system": "unit_test",
        "columns": [{"name": "id", "type": "int"}],
    }
    r = client.post("/datasets", json=payload)
    # dataset may already exist; accept 200 or 400
    assert r.status_code in (200, 400)

    # search for the table name
    r = client.get("/search", params={"q": "test_table"})
    assert r.status_code == 200
    data = r.json()
    assert "results" in data


def test_lineage_cycle_protection():
    # create two datasets
    a = {"fqn": "a.b.c.ds_a", "columns": []}
    b = {"fqn": "a.b.c.ds_b", "columns": []}
    client.post("/datasets", json=a)
    client.post("/datasets", json=b)

    # add a->b
    r = client.post("/lineage", json={"upstream_fqn": a["fqn"], "downstream_fqn": b["fqn"]})
    assert r.status_code in (200, 400)

    # adding b->a should be rejected as cycle
    r2 = client.post("/lineage", json={"upstream_fqn": b["fqn"], "downstream_fqn": a["fqn"]})
    assert r2.status_code in (400, 404)
