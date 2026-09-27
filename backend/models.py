from sqlalchemy import (
  Column, Integer, String, Boolean, DateTime, Date,
  DECIMAL, ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Store(Base):
  __tablename__ = "STORE"

  store_id = Column(Integer, primary_key=True, autoincrement=True)
  store_code = Column(String(20), nullable=False, unique=True)
  store_name = Column(String(100), nullable=False)
  address = Column(String(255))
  is_closed = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Staff(Base):
  __tablename__ = "STAFF"

  staff_id = Column(Integer, primary_key=True, autoincrement=True)
  store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
  staff_code = Column(String(20), nullable=False, unique=True)
  staff_name = Column(String(100), nullable=False)
  password_hash = Column(String(255), nullable=False)
  role = Column(Enum("general", "admin", name="staff_role"), nullable=False, default="general")
  is_active = Column(Boolean, nullable=False, default=True)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

  __table_args__ = (
    Index("idx_staff_store_id", "store_id"),
  )


class Member(Base):
  __tablename__ = "MEMBER"

  member_id = Column(Integer, primary_key=True, autoincrement=True)
  member_code = Column(String(30), nullable=False, unique=True)
  member_name = Column(String(100), nullable=False)
  phone_number = Column(String(20))
  address = Column(String(255))
  gender = Column(Enum("male", "female", "other", name="member_gender"))
  birth_date = Column(Date)
  is_withdrawn = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Product(Base):
  __tablename__ = "PRODUCT"

  product_id = Column(Integer, primary_key=True, autoincrement=True)
  product_code = Column(String(30), nullable=False, unique=True)
  product_name = Column(String(150), nullable=False)
  tax_category = Column(Enum("standard", "reduced", name="tax_category"), nullable=False, default="standard")
  is_abolished = Column(Boolean, nullable=False, default=False)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class ProductStore(Base):
  __tablename__ = "PRODUCT_STORE"

  product_store_id = Column(Integer, primary_key=True, autoincrement=True)
  store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
  product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
  unit_price = Column(DECIMAL(10, 2), nullable=False)
  is_available = Column(Boolean, nullable=False, default=True)
  effective_from = Column(Date, nullable=False)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

  __table_args__ = (
    UniqueConstraint("store_id", "product_id", name="uq_store_product"),
    Index("idx_ps_store_id", "store_id"),
  )


class TaxRate(Base):
  __tablename__ = "TAX_RATE"

  tax_rate_id = Column(Integer, primary_key=True, autoincrement=True)
  rate = Column(DECIMAL(5, 2), nullable=False)
  effective_from = Column(Date, nullable=False)
  effective_to = Column(Date)
  created_at = Column(DateTime, nullable=False, server_default=func.now())


class Transaction(Base):
  __tablename__ = "TRANSACTION"

  transaction_id = Column(Integer, primary_key=True, autoincrement=True)
  store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
  staff_id = Column(Integer, ForeignKey("STAFF.staff_id"), nullable=False)
  member_id = Column(Integer, ForeignKey("MEMBER.member_id"))
  idempotency_key = Column(String(100), nullable=False, unique=True)
  total_excl_tax = Column(DECIMAL(10, 2), nullable=False)
  total_incl_tax = Column(DECIMAL(10, 2), nullable=False)
  discount_amount = Column(DECIMAL(10, 2), nullable=False, default=0)
  transacted_at = Column(DateTime, nullable=False, server_default=func.now())

  __table_args__ = (
    Index("idx_tx_store_id", "store_id"),
  )


class TransactionItem(Base):
  __tablename__ = "TRANSACTION_ITEM"

  transaction_item_id = Column(Integer, primary_key=True, autoincrement=True)
  transaction_id = Column(Integer, ForeignKey("TRANSACTION.transaction_id"), nullable=False)
  product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
  quantity = Column(Integer, nullable=False)
  unit_price = Column(DECIMAL(10, 2), nullable=False)
  tax_rate = Column(DECIMAL(5, 2), nullable=False)
  discount_amount = Column(DECIMAL(10, 2), nullable=False, default=0)
  subtotal_excl_tax = Column(DECIMAL(10, 2), nullable=False)


class DiscountRule(Base):
  __tablename__ = "DISCOUNT_RULE"

  discount_rule_id = Column(Integer, primary_key=True, autoincrement=True)
  store_id = Column(Integer, ForeignKey("STORE.store_id"))
  product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
  discount_type = Column(Enum("rate", "amount", name="discount_type"), nullable=False)
  discount_value = Column(DECIMAL(10, 2), nullable=False)
  member_only = Column(Boolean, nullable=False, default=True)
  effective_from = Column(Date, nullable=False)
  effective_to = Column(Date)
  is_active = Column(Boolean, nullable=False, default=True)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

  __table_args__ = (
    Index("idx_dr_store_id", "store_id"),
    Index("idx_dr_product_id", "product_id"),
  )