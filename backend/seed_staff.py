# scripts/seed_staff.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Store
from app.core.security import get_password_hash
from models import Staff

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

try:
  # 既存のstore_idを取得（STOREはすでに投入済みのため）
  store1 = session.query(Store).filter(Store.store_code == "ST001").first()
  store2 = session.query(Store).filter(Store.store_code == "ST002").first()

  staff1 = Staff(
    store_id=store1.store_id, staff_code="S001", staff_name="一般スタッフA",
    password_hash=get_password_hash("password123"), role="general"
  )
  staff2 = Staff(
    store_id=store2.store_id, staff_code="A001", staff_name="管理者A",
    password_hash=get_password_hash("adminpass456"), role="admin"
  )
  session.add_all([staff1, staff2])

  session.commit()
  print("STAFFサンプルデータの投入が完了しました🎉")

except Exception as e:
  session.rollback()
  print(f"エラーが発生したためロールバックしました: {e}")

finally:
  session.close()