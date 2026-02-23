from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from datetime import datetime
from app.db.session import Base, engine

def _json_type():
    # Use JSONB on Postgres, JSON otherwise
    if engine.dialect.name == "postgresql":
        return JSONB
    return JSON

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(32), default="viewer")  # admin / axis / viewer
    stripe_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assignments: Mapped[list["CaseAssignment"]] = relationship(back_populates="axis_user")

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    plan: Mapped[str] = mapped_column(String(32), default="none")  # professional / enterprise / none
    stripe_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    subscription_status: Mapped[str] = mapped_column(String(32), default="inactive")  # active/inactive/past_due/canceled
    current_period_end: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cases: Mapped[list["Case"]] = relationship(back_populates="company")

class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    industry: Mapped[str] = mapped_column(String(64), default="generic")
    title: Mapped[str] = mapped_column(String(256), default="New Case")
    input_payload: Mapped[dict] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="cases")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="case")
    assignments: Mapped[list["CaseAssignment"]] = relationship(back_populates="case")

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    version: Mapped[str] = mapped_column(String(32), default="3.1.0")
    result: Mapped[dict] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship(back_populates="analyses")

class CaseAssignment(Base):
    __tablename__ = "case_assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    axis_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship(back_populates="assignments")
    axis_user: Mapped["User"] = relationship(back_populates="assignments")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
