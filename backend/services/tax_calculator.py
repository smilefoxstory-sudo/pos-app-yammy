from decimal import Decimal, ROUND_DOWN

# 税率マスタ（将来的にはDBのTaxRateテーブルに移行しやすい形にしておく）
TAX_RATES = {
  "standard": Decimal("0.10"),  # 標準税率
  "reduced": Decimal("0.08"),   # 軽減税率
}

def calculate_tax_included_price(subtotal_excl_tax, tax_rate):
  """
  税抜金額と税率（数値）から税込金額を計算する
  """
  return subtotal_excl_tax * (1 + tax_rate)