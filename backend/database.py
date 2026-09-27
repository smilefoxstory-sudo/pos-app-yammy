import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
  DATABASE_URL,
  connect_args={"ssl": {"ssl_mode": "REQUIRED"}}
)
SessionLocal = sessionmaker(bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()