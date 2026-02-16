from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from models import Base
from schemas import (
    DatasetCreate,
    DatasetResponse,
    DatasetUpdate,
    LineageCreate,
    SearchResult,
    ColumnModel,
)
from models.metadata import Dataset, DatasetColumn, Lineage
from typing import List


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Metadata Service")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health():
    return {"status": "ok"}


def parse_fqn(fqn: str):
    """Parse a fully-qualified name into components.
    Expecting: connection.database.schema.table_name
    """
    parts = fqn.split(".")
    if len(parts) < 1:
        raise ValueError("Invalid FQN")
    # Fill from the right: table, schema, database, connection
    table = parts[-1] if len(parts) >= 1 else None
    schema = parts[-2] if len(parts) >= 2 else None
    database = parts[-3] if len(parts) >= 3 else None
    connection = parts[-4] if len(parts) >= 4 else None
    return {
        "fqn": fqn,
        "connection": connection,
        "database": database,
        "schema": schema,
        "table_name": table,
    }


def get_dataset_by_fqn(db: Session, fqn: str):
    return db.query(Dataset).filter(Dataset.fqn == fqn).first()


def immediate_upstream_fqns(db: Session, dataset: Dataset) -> List[str]:
    return [link.upstream_dataset.fqn for link in dataset.upstream_links]


def immediate_downstream_fqns(db: Session, dataset: Dataset) -> List[str]:
    return [link.downstream_dataset.fqn for link in dataset.downstream_links]


@app.post("/datasets", response_model=DatasetResponse)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    """Create a dataset with optional columns."""
    if get_dataset_by_fqn(db, payload.fqn):
        raise HTTPException(status_code=400, detail="Dataset with this FQN already exists")

    parts = parse_fqn(payload.fqn)
    ds = Dataset(
        fqn=payload.fqn,
        connection=parts.get("connection"),
        database=parts.get("database"),
        schema=parts.get("schema"),
        table_name=parts.get("table_name"),
        description=payload.description,
        source_system=payload.source_system,
    )
    db.add(ds)
    db.flush()  # ensure ds.id

    # Add columns if provided
    for col in payload.columns or []:
        c = DatasetColumn(dataset_id=ds.id, name=col.name, type=col.type)
        db.add(c)

    db.commit()
    db.refresh(ds)

    return DatasetResponse(
        id=ds.id,
        fqn=ds.fqn,
        connection=ds.connection,
        database=ds.database,
        schema=ds.schema,
        table_name=ds.table_name,
        description=ds.description,
        source_system=ds.source_system,
        columns=[ColumnModel(name=c.name, type=c.type) for c in ds.columns],
        upstream=immediate_upstream_fqns(db, ds),
        downstream=immediate_downstream_fqns(db, ds),
        created_at=ds.created_at,
        updated_at=ds.updated_at,
    )


@app.get("/datasets/{fqn}", response_model=DatasetResponse)
def get_dataset(fqn: str, db: Session = Depends(get_db)):
    ds = get_dataset_by_fqn(db, fqn)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetResponse(
        id=ds.id,
        fqn=ds.fqn,
        connection=ds.connection,
        database=ds.database,
        schema=ds.schema,
        table_name=ds.table_name,
        description=ds.description,
        source_system=ds.source_system,
        columns=[ColumnModel(name=c.name, type=c.type) for c in ds.columns],
        upstream=immediate_upstream_fqns(db, ds),
        downstream=immediate_downstream_fqns(db, ds),
        created_at=ds.created_at,
        updated_at=ds.updated_at,
    )


@app.get("/datasets", response_model=List[DatasetResponse])
def list_datasets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rows = db.query(Dataset).offset(skip).limit(limit).all()
    results = []
    for ds in rows:
        results.append(
            DatasetResponse(
                id=ds.id,
                fqn=ds.fqn,
                connection=ds.connection,
                database=ds.database,
                schema=ds.schema,
                table_name=ds.table_name,
                description=ds.description,
                source_system=ds.source_system,
                columns=[ColumnModel(name=c.name, type=c.type) for c in ds.columns],
                upstream=immediate_upstream_fqns(db, ds),
                downstream=immediate_downstream_fqns(db, ds),
                created_at=ds.created_at,
                updated_at=ds.updated_at,
            )
        )
    return results


def creates_cycle(db: Session, upstream_id: int, downstream_id: int) -> bool:
    """Return True if adding upstream -> downstream would create a cycle."""
    # We must check whether downstream can reach upstream through existing downstream links.
    stack = [downstream_id]
    visited = set()
    while stack:
        current = stack.pop()
        if current == upstream_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        # find nodes that are downstream of current (i.e., edges current -> next)
        links = db.query(Lineage).filter(Lineage.upstream_id == current).all()
        for link in links:
            stack.append(link.downstream_id)
    return False


@app.post("/lineage")
def add_lineage(payload: LineageCreate, db: Session = Depends(get_db)):
    """Create a lineage edge upstream_fqn -> downstream_fqn, preventing cycles."""
    up = get_dataset_by_fqn(db, payload.upstream_fqn)
    down = get_dataset_by_fqn(db, payload.downstream_fqn)
    if not up or not down:
        raise HTTPException(status_code=404, detail="Upstream or downstream dataset not found")

    if creates_cycle(db, up.id, down.id):
        raise HTTPException(status_code=400, detail="Adding this lineage would create a cycle")

    # Prevent duplicate
    exists = db.query(Lineage).filter(Lineage.upstream_id == up.id, Lineage.downstream_id == down.id).first()
    if exists:
        return {"message": "Lineage already exists"}

    link = Lineage(upstream_id=up.id, downstream_id=down.id)
    db.add(link)
    db.commit()
    return {"message": "Lineage added"}


@app.get("/lineage/{fqn}")
def get_lineage(fqn: str, db: Session = Depends(get_db)):
    ds = get_dataset_by_fqn(db, fqn)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"upstream": immediate_upstream_fqns(db, ds), "downstream": immediate_downstream_fqns(db, ds)}


@app.get("/search", response_model=SearchResult)
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Search datasets by table name (priority 1), column name (2), schema (3), database (4).
    Results are deduplicated and ordered by priority.
    """
    term = f"%{q}%"
    results = []
    seen = set()

    # Priority 1: table name
    table_matches = db.query(Dataset).filter(Dataset.table_name.ilike(term)).all()
    for ds in table_matches:
        if ds.fqn in seen:
            continue
        seen.add(ds.fqn)
        results.append(ds)

    # Priority 2: column name
    col_matches = (
        db.query(Dataset)
        .join(DatasetColumn, Dataset.id == DatasetColumn.dataset_id)
        .filter(DatasetColumn.name.ilike(term))
        .all()
    )
    for ds in col_matches:
        if ds.fqn in seen:
            continue
        seen.add(ds.fqn)
        results.append(ds)

    # Priority 3: schema
    schema_matches = db.query(Dataset).filter(Dataset.schema.ilike(term)).all()
    for ds in schema_matches:
        if ds.fqn in seen:
            continue
        seen.add(ds.fqn)
        results.append(ds)

    # Priority 4: database
    db_matches = db.query(Dataset).filter(Dataset.database.ilike(term)).all()
    for ds in db_matches:
        if ds.fqn in seen:
            continue
        seen.add(ds.fqn)
        results.append(ds)

    payloads = []
    for ds in results:
        payloads.append(
            DatasetResponse(
                id=ds.id,
                fqn=ds.fqn,
                connection=ds.connection,
                database=ds.database,
                schema=ds.schema,
                table_name=ds.table_name,
                description=ds.description,
                source_system=ds.source_system,
                columns=[ColumnModel(name=c.name, type=c.type) for c in ds.columns],
                upstream=immediate_upstream_fqns(db, ds),
                downstream=immediate_downstream_fqns(db, ds),
                created_at=ds.created_at,
                updated_at=ds.updated_at,
            )
        )

    return SearchResult(results=payloads)
