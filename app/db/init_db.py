import os
from sqlalchemy import inspect
from app.db.session import engine, Base
from app.db import models  # noqa: F401

def init_db():
    Base.metadata.create_all(bind=engine)

def has_tables() -> bool:
    insp = inspect(engine)
    return len(insp.get_table_names()) > 0
