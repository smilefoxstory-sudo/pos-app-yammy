const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export async function login(staffCode: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ staff_code: staffCode, password: password }),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    throw new Error(errorBody?.detail || "ログインに失敗しました");
  }

  return res.json();
}

export type TransactionItemInput = {
  product_code: string;
  quantity: number;
};

export type TransactionPreviewRequest = {
  store_id: number;
  staff_id: number;
  member_id: number | null;
  idempotency_key: string;
  items: TransactionItemInput[];
};

export type TransactionPreviewItem = {
  product_id: number;
  product_code: string; // ★追加: フロント側でのproduct_code突き合わせ用
  product_name: string;
  unit_price: string;
  quantity: number;
  tax_rate: string;
  discount_amount: string;
  subtotal_excl_tax: string;
};

export type TransactionPreviewResponse = {
  items: TransactionPreviewItem[];
  total_excl_tax: string;
  total_incl_tax: string;
  discount_amount: string;
};

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export async function previewTransaction(
  payload: TransactionPreviewRequest
): Promise<TransactionPreviewResponse> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("ログイン情報が見つかりません。再度ログインしてください");
  }

  const res = await fetch(`${API_BASE_URL}/transactions/preview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    throw new Error(errorBody?.detail || "プレビューの取得に失敗しました");
  }

  return res.json();
}