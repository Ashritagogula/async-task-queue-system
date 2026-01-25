from sqlalchemy import Column, String, Text, Enum, TIMESTAMP, JSON
from sqlalchemy.sql import func
from src.db.database import Base   # ✅ USE SHARED BASE

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    status = Column(
        Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED"),
        nullable=False,
        default="PENDING"
    )

    # ✅ Safe mapping for reserved word
    task_metadata = Column("metadata", JSON, nullable=True)

    # ✅ Proper timestamps
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        TIMESTAMP,
        onupdate=func.now()
    )

    completed_at = Column(TIMESTAMP, nullable=True)
