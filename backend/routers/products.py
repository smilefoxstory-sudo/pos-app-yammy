from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Product, ProductStore
from services.tax_calculator import calculate_tax_included_price
from security import get_current_staff

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/{product_code}")
def get_product(
  product_code: str,
  store_id: int,
  db: Session = Depends(get_db),
  current_staff: dict = Depends(get_current_staff),
):
  # 1. PRODUCTテーブルからproduct_codeで検索
  product = db.query(Product).filter(Product.product_code == product_code).first()
  if not product:
    raise HTTPException(status_code=404, detail="商品が見つかりません")

  # 2. PRODUCT_STOREテーブルから該当店舗の単価を検索
  product_store = db.query(ProductStore).filter(
    ProductStore.product_id == product.product_id,
    ProductStore.store_id == store_id
  ).first()
  if not product_store:
    raise HTTPException(status_code=404, detail="この店舗で取り扱いのない商品です")

  tax_included_price = calculate_tax_included_price(
    product_store.unit_price, product.tax_category
  )

  return {
    "product_id": product.product_id,
    "product_code": product.product_code,
    "product_name": product.product_name,
    "tax_category": product.tax_category,
    "unit_price": float(product_store.unit_price),
    "tax_included_price": float(tax_included_price),
  }