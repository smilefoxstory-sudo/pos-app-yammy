from decimal import Decimal
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Product, ProductStore, Transaction, TransactionItem
from services.tax_calculator import calculate_tax_included_price
from services.discount_calculator import calculate_discount, get_tax_rate
from schemas import TransactionRequest, TransactionPreviewResponse, TransactionConfirmResponse
from security import get_current_staff

router = APIRouter()


def _build_transaction_items(db: Session, store_id: int, is_member: bool, items):
  """
  リクエストされた商品リストから、明細情報（商品名・単価・数量・割引・小計）を組み立てる
  """
  result_items = []
  total_excl_tax = Decimal("0")
  total_discount = Decimal("0")

  for item in items:
    product = (
      db.query(Product)
      .filter(Product.product_code == item.product_code)
      .first()
    )
    if not product:
      raise HTTPException(
        status_code=404,
        detail=f"商品コード {item.product_code} が見つかりません",
      )

    product_store = (
      db.query(ProductStore)
      .filter(
        ProductStore.product_id == product.product_id,
        ProductStore.store_id == store_id,
      )
      .first()
    )
    if not product_store:
      raise HTTPException(
        status_code=404,
        detail=f"商品コード {item.product_code} は店舗ID {store_id} で取り扱いがありません",
      )

    unit_price = product_store.unit_price
    quantity = item.quantity
    tax_rate = get_tax_rate(product.tax_category)

    discount_amount = calculate_discount(
      db=db,
      product_id=product.product_id,
      store_id=store_id,
      unit_price=unit_price,
      quantity=quantity,
      is_member=is_member,
      transaction_date=date.today(),
    )

    subtotal_excl_tax = (unit_price * quantity) - discount_amount

    result_items.append({
      "product_id": product.product_id,
      "product_code": product.product_code,  # ★追加: フロント側でのproduct_code突き合わせ用
      "product_name": product.product_name,
      "unit_price": unit_price,
      "quantity": quantity,
      "tax_rate": tax_rate,
      "discount_amount": discount_amount,
      "subtotal_excl_tax": subtotal_excl_tax,
    })

    total_excl_tax += subtotal_excl_tax
    total_discount += discount_amount

  return result_items, total_excl_tax, total_discount


@router.post("/transactions/preview", response_model=TransactionPreviewResponse)
def preview_transaction(
  request: TransactionRequest,
  db: Session = Depends(get_db),
  current_staff: dict = Depends(get_current_staff),
):
  """
  会計内容の計算結果のみを返す（DB保存なし）
  """
  is_member = request.member_id is not None

  items, total_excl_tax, total_discount = _build_transaction_items(
    db, request.store_id, is_member, request.items
  )

  total_incl_tax = sum(
    calculate_tax_included_price(item["subtotal_excl_tax"], item["tax_rate"])
    for item in items
  )

  return {
    "items": items,
    "total_excl_tax": total_excl_tax,
    "total_incl_tax": total_incl_tax,
    "discount_amount": total_discount,
  }


@router.post("/transactions/confirm", response_model=TransactionConfirmResponse)
def confirm_transaction(
  request: TransactionRequest,
  db: Session = Depends(get_db),
  current_staff: dict = Depends(get_current_staff),
):
  """
  会計内容を計算した上で、TRANSACTION・TRANSACTION_ITEMへ保存する
  idempotency_keyで二重送信を防止する
  """
  existing = (
    db.query(Transaction)
    .filter(Transaction.idempotency_key == request.idempotency_key)
    .first()
  )
  if existing:
    return {
      "transaction_id": existing.transaction_id,
      "total_excl_tax": existing.total_excl_tax,
      "total_incl_tax": existing.total_incl_tax,
      "discount_amount": existing.discount_amount,
    }

  is_member = request.member_id is not None

  items, total_excl_tax, total_discount = _build_transaction_items(
    db, request.store_id, is_member, request.items
  )

  total_incl_tax = sum(
    calculate_tax_included_price(item["subtotal_excl_tax"], item["tax_rate"])
    for item in items
  )

  transaction = Transaction(
    store_id=request.store_id,
    staff_id=request.staff_id,
    member_id=request.member_id,
    idempotency_key=request.idempotency_key,
    total_excl_tax=total_excl_tax,
    total_incl_tax=total_incl_tax,
    discount_amount=total_discount,
  )
  db.add(transaction)
  db.flush()  # transaction_idを採番するためINSERTを先行実行

  for item in items:
    transaction_item = TransactionItem(
      transaction_id=transaction.transaction_id,
      product_id=item["product_id"],
      quantity=item["quantity"],
      unit_price=item["unit_price"],
      tax_rate=item["tax_rate"],
      discount_amount=item["discount_amount"],
      subtotal_excl_tax=item["subtotal_excl_tax"],
    )
    db.add(transaction_item)

  db.commit()
  db.refresh(transaction)

  return {
    "transaction_id": transaction.transaction_id,
    "total_excl_tax": transaction.total_excl_tax,
    "total_incl_tax": transaction.total_incl_tax,
    "discount_amount": transaction.discount_amount,
  }