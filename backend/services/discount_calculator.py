from decimal import Decimal
from datetime import date
from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import DiscountRule

TAX_RATE_MAP = {
  "standard": Decimal("0.10"),
  "reduced": Decimal("0.08"),
}


def get_tax_rate(tax_category: str) -> Decimal:
  """
  tax_category（standard/reduced）を税率の数値に変換する
  """
  if tax_category not in TAX_RATE_MAP:
    raise ValueError(f"不明な税区分です: {tax_category}")
  return TAX_RATE_MAP[tax_category]


def get_applicable_discount_rules(
  db: Session,
  product_id: int,
  store_id: int,
  is_member: bool,
  transaction_date: date,
):
  """
  対象商品・店舗・会員区分・会計日に該当する割引ルールの候補を取得する
  """
  query = db.query(DiscountRule).filter(
    DiscountRule.product_id == product_id,
    or_(
      DiscountRule.store_id == store_id,
      DiscountRule.store_id.is_(None),
    ),
    DiscountRule.effective_from <= transaction_date,
    or_(
      DiscountRule.effective_to >= transaction_date,
      DiscountRule.effective_to.is_(None),
    ),
    DiscountRule.is_active == True,
  )

  if not is_member:
    query = query.filter(DiscountRule.member_only == False)

  return query.all()


def calculate_discount(
  db: Session,
  product_id: int,
  store_id: int,
  unit_price: Decimal,
  quantity: int,
  is_member: bool,
  transaction_date: date,
) -> Decimal:
  """
  商品1明細分の割引額を計算する
  複数の割引ルールが該当する場合は、割引額が最大のものを採用する
  """
  candidates = get_applicable_discount_rules(
    db, product_id, store_id, is_member, transaction_date
  )

  if not candidates:
    return Decimal("0")

  discount_amounts = []
  for rule in candidates:
    if rule.discount_type == "rate":
      amount = unit_price * quantity * (rule.discount_value / Decimal("100"))
    else:  # amount
      amount = rule.discount_value * quantity
    discount_amounts.append(amount)

  return max(discount_amounts)