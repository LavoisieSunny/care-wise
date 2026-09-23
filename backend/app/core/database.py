from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "carewise.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLite now; swap this one line for Postgres later e.g.
# "postgresql://user:pass@host:5432/carewise" — nothing else in this file changes.
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-only flag, no-op on Postgres
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PolicyRecord(Base):
    __tablename__ = "policies"
    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, index=True, nullable=True)   # ready for Step 2 (auth) later
    insurer_name = Column(String, index=True)
    policy_name = Column(String)
    data_json = Column(Text)          # full PolicyDetails, stored as JSON for now
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserRecord(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)
