from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Dataset(Base):
    """Represents a dataset identified by a fully-qualified name (FQN)."""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    fqn = Column(String(1024), unique=True, index=True, nullable=False)
    connection = Column(String(255), nullable=True, index=True)
    database = Column(String(255), nullable=True, index=True)
    schema = Column(String(255), nullable=True, index=True)
    table_name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    source_system = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    upstream_links = relationship(
        "Lineage",
        foreign_keys="Lineage.downstream_id",
        back_populates="downstream_dataset",
        cascade="all, delete-orphan",
    )
    downstream_links = relationship(
        "Lineage",
        foreign_keys="Lineage.upstream_id",
        back_populates="upstream_dataset",
        cascade="all, delete-orphan",
    )


class DatasetColumn(Base):
    __tablename__ = "columns"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(255), nullable=True)

    dataset = relationship("Dataset", back_populates="columns")


class Lineage(Base):
    __tablename__ = "lineage"
    id = Column(Integer, primary_key=True, index=True)
    upstream_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    downstream_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)

    upstream_dataset = relationship("Dataset", foreign_keys=[upstream_id], back_populates="downstream_links")
    downstream_dataset = relationship("Dataset", foreign_keys=[downstream_id], back_populates="upstream_links")

    __table_args__ = (UniqueConstraint("upstream_id", "downstream_id", name="uq_lineage_up_down"),)
