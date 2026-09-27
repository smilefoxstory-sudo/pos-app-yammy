from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class TransactionItemRequest(BaseModel):
  product_code: str
  quantity: int


class TransactionRequest(BaseModel):
  store_id: int
  staff_id: int
  member_id: Optional[int] = None
  idempotency_key: str
  items: List[TransactionItemRequest]


class TransactionItemResponse(BaseModel):
  product_id: int
  product_code: str  # ★追加: フロント側でのproduct_code突き合わせ用
  product_name: str
  unit_price: Decimal
  quantity: int
  tax_rate: Decimal
  discount_amount: Decimal
  subtotal_excl_tax: Decimal


class TransactionPreviewResponse(BaseModel):
  items: List[TransactionItemResponse]
  total_excl_tax: Decimal
  total_incl_tax: Decimal
  discount_amount: Decimal


class TransactionConfirmResponse(BaseModel):
  transaction_id: int
  total_excl_tax: Decimal
  total_incl_tax: Decimal
  discount_amount: Decimal