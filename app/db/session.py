from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def make_engine(database_url: str):
    # SQLite + FastAPI の定番（別スレッドアクセス許可）
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
        pool_pre_ping=True,
    )

def make_session_local(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

