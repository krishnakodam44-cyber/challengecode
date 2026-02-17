from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ColumnModel(BaseModel):
    name: str
    type: Optional[str] = None


class DatasetCreate(BaseModel):
    fqn: str
    description: Optional[str] = None
    source_system: Optional[str] = None
    columns: Optional[List[ColumnModel]] = []


class DatasetUpdate(BaseModel):
    description: Optional[str] = None
    source_system: Optional[str] = None
    columns: Optional[List[ColumnModel]] = None


class DatasetResponse(BaseModel):
    id: int
    fqn: str
    connection: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    table_name: Optional[str] = None
    description: Optional[str] = None
    source_system: Optional[str] = None
    columns: List[ColumnModel] = []
    upstream: List[str] = []
    downstream: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LineageCreate(BaseModel):
    upstream_fqn: str
    downstream_fqn: str


class SearchResult(BaseModel):
    results: List[DatasetResponse]
