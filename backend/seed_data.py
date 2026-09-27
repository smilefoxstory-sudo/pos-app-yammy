import os
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
  Store, Staff, Member, Product, ProductStore,
  TaxRate, DiscountRule
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

try:
  # 1. STORE
  store1 = Store(store_code="ST001", store_name="Yummy 渋谷店", address="東京都渋谷区1-1-1")
  store2 = Store(store_code="ST002", store_name="Yummy 新宿店", address="東京都新宿区2-2-2")
  session.add_all([store1, store2])
  session.flush()  # store_idを確定させる

  # 2. STAFF
  staff1 = Staff(
    store_id=store1.store_id, staff_code="STF001", staff_name="山田太郎",
    password_hash="hashed_password_1", role="admin"
  )
  staff2 = Staff(
    store_id=store2.store_id, staff_code="STF002", staff_name="佐藤花子",
    password_hash="hashed_password_2", role="general"
  )
  session.add_all([staff1, staff2])

  # 3. MEMBER
  member1 = Member(
    member_code="MEM001", member_name="鈴木一郎", phone_number="090-1111-2222",
    gender="male", birth_date=date(1985, 4, 1)
  )
  session.add(member1)

  # 4. PRODUCT
  product1 = Product(product_code="4901234567890", product_name="おにぎり 鮭", tax_category="reduced")
  product2 = Product(product_code="4901234567891", product_name="お茶 500ml", tax_category="reduced")
  product3 = Product(product_code="4901234567892", product_name="イタリア産パスタ", tax_category="reduced")
  session.add_all([product1, product2, product3])
  session.flush()  # product_idを確定させる

  # 5. PRODUCT_STORE
  ps1 = ProductStore(store_id=store1.store_id, product_id=product1.product_id, unit_price=150.00, effective_from=date(2026, 9, 1))
  ps2 = ProductStore(store_id=store1.store_id, product_id=product2.product_id, unit_price=120.00, effective_from=date(2026, 9, 1))
  ps3 = ProductStore(store_id=store2.store_id, product_id=product3.product_id, unit_price=300.00, effective_from=date(2026, 9, 1))
  session.add_all([ps1, ps2, ps3])

  # 6. TAX_RATE
  tax1 = TaxRate(rate=10.00, effective_from=date(2019, 10, 1))
  tax2 = TaxRate(rate=8.00, effective_from=date(2019, 10, 1))
  session.add_all([tax1, tax2])

  # 7. DISCOUNT_RULE（会員限定＋全員対象の両パターン）
  dr1 = DiscountRule(
    store_id=None, product_id=product2.product_id, discount_type="amount",
    discount_value=20.00, member_only=True,
    effective_from=date(2026, 9, 1), effective_to=date(2026, 9, 30)
  )
  dr2 = DiscountRule(
    store_id=None, product_id=product3.product_id, discount_type="rate",
    discount_value=15.00, member_only=False,
    effective_from=date(2026, 9, 1), effective_to=date(2026, 9, 30)
  )
  session.add_all([dr1, dr2])

  session.commit()
  print("サンプルデータの投入が完了しました🎉")

except Exception as e:
  session.rollback()
  print(f"エラーが発生したためロールバックしました: {e}")

finally:
  session.close()