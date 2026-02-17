import json
import urllib.request

BASE = "http://localhost:8000"


def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            print(f"POST {path} -> {resp.status}\n{body}\n")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"POST {path} -> {e.code}\n{body}\n")
    except Exception as e:
        print(f"POST {path} -> ERROR {e}\n")


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as resp:
            body = resp.read().decode()
            print(f"GET {path} -> {resp.status}\n{body}\n")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"GET {path} -> {e.code}\n{body}\n")
    except Exception as e:
        print(f"GET {path} -> ERROR {e}\n")


if __name__ == '__main__':
    # Create datasets
    ds_a = {
        "fqn": "snowflake_prod.bi_team.bronze.orders_raw",
        "description": "raw orders",
        "source_system": "snowflake",
        "columns": [{"name": "order_id", "type": "int"}, {"name": "order_ts", "type": "timestamp"}]
    }
    ds_b = {
        "fqn": "snowflake_prod.bi_team.silver.orders_clean",
        "description": "clean orders",
        "source_system": "snowflake",
        "columns": [{"name": "order_id", "type": "int"}, {"name": "amount", "type": "float"}]
    }
    ds_c = {
        "fqn": "snowflake_prod.bi_team.gold.orders_aggregated",
        "description": "aggregated orders",
        "source_system": "snowflake",
        "columns": [{"name": "order_id", "type": "int"}, {"name": "total", "type": "float"}]
    }

    post("/datasets", ds_a)
    post("/datasets", ds_b)
    post("/datasets", ds_c)

    # Add lineage A -> B, B -> C
    post("/lineage", {"upstream_fqn": ds_a["fqn"], "downstream_fqn": ds_b["fqn"]})
    post("/lineage", {"upstream_fqn": ds_b["fqn"], "downstream_fqn": ds_c["fqn"]})

    # Attempt invalid cycle C -> A
    post("/lineage", {"upstream_fqn": ds_c["fqn"], "downstream_fqn": ds_a["fqn"]})

    # Search
    get("/search?q=order")
