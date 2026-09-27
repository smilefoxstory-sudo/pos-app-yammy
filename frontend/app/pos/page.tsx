"use client";

import { useEffect, useRef, useState } from "react";
import {
  previewTransaction,
  TransactionItemInput,
  TransactionPreviewResponse,
} from "@/app/lib/api";
import { Html5Qrcode } from "html5-qrcode";

type CartItem = TransactionItemInput;

const SCANNER_ELEMENT_ID = "barcode-scanner";

export default function PosPage() {
  const [productCode, setProductCode] = useState("");
  const [inputMode, setInputMode] = useState<"manual" | "camera">("manual");
  const [cartItems, setCartItems] = useState<Map<string, CartItem>>(new Map());
  const [preview, setPreview] = useState<TransactionPreviewResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isScannerReady, setIsScannerReady] = useState(false);

  const scannerRef = useRef<Html5Qrcode | null>(null);
  const isScanningRef = useRef(false);

  const fetchPreview = async (
    items: Map<string, CartItem>,
    previousItems: Map<string, CartItem>
  ) => {
    const itemList = Array.from(items.values());

    if (itemList.length === 0) {
      setPreview(null);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const result = await previewTransaction({
        store_id: 1,
        staff_id: 1,
        member_id: null,
        idempotency_key: `preview-${Date.now()}`,
        items: itemList.map(({ product_code, quantity }) => ({
          product_code,
          quantity,
        })),
      });

      setPreview(result);
    } catch (err) {
      // エラー時はカートの変更をロールバック(直前の状態に戻す)
      setCartItems(previousItems);

      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("予期しないエラーが発生しました");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const addProductCode = (code: string) => {
    if (!code.trim()) return;

    const previousItems = cartItems;
    const newMap = new Map(cartItems);
    const existing = newMap.get(code);

    if (existing) {
      newMap.set(code, { ...existing, quantity: existing.quantity + 1 });
    } else {
      newMap.set(code, { product_code: code, quantity: 1 });
    }

    setCartItems(newMap);
    setProductCode("");
    fetchPreview(newMap, previousItems);
  };

  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault();
    addProductCode(productCode);
  };

  const handleRemoveItem = (targetProductCode: string) => {
    const previousItems = cartItems;
    const newMap = new Map(cartItems);
    newMap.delete(targetProductCode);
    setCartItems(newMap);
    fetchPreview(newMap, previousItems);
  };

  // カメラモード切り替え時に、バーコードスキャナーの起動・停止を制御
  useEffect(() => {
    if (inputMode !== "camera") {
      return;
    }

    const scanner = new Html5Qrcode(SCANNER_ELEMENT_ID);
    scannerRef.current = scanner;
    isScanningRef.current = true;

    scanner
      .start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 150 } },
        (decodedText) => {
          // 連続で同じコードを読み込みすぎないよう簡易ガード
          if (isScanningRef.current) {
            addProductCode(decodedText);
          }
        },
        () => {
          // 読み取り失敗(未検出)は毎フレーム発生しうるため無視
        }
      )
      .then(() => setIsScannerReady(true))
      .catch((err) => {
        console.error(err);
        setErrorMessage("カメラを起動できませんでした。カメラの使用を許可してください");
      });

    return () => {
      isScanningRef.current = false;
      scanner
        .stop()
        .then(() => scanner.clear())
        .catch(() => {
          // 停止処理は失敗しても無視して問題ない
        });
      setIsScannerReady(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inputMode]);

  return (
    <div
      style={{
        maxWidth: 1100,
        margin: "40px auto",
        padding: 24,
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <h1
        style={{
          fontSize: 28,
          marginBottom: 24,
          color: "#2563eb",
          fontWeight: 800,
          letterSpacing: "-0.02em",
        }}
      >
        Yammy POS
      </h1>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 24,
          alignItems: "flex-start",
        }}
      >
        {/* 左カラム: 商品コード入力 */}
        <div style={{ flex: "1 1 380px", minWidth: 320 }}>
          <div
            style={{
              backgroundColor: "#ffffff",
              borderRadius: 12,
              padding: 20,
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              marginBottom: 24,
            }}
          >
            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
              <button
                type="button"
                onClick={() => setInputMode("manual")}
                style={{
                  flex: 1,
                  padding: 10,
                  borderRadius: 8,
                  border: "none",
                  cursor: "pointer",
                  fontWeight: 600,
                  backgroundColor: inputMode === "manual" ? "#2563eb" : "#e5e7eb",
                  color: inputMode === "manual" ? "#fff" : "#374151",
                  transition: "background-color 0.2s",
                }}
              >
                ⌨️ 手入力
              </button>
              <button
                type="button"
                onClick={() => setInputMode("camera")}
                style={{
                  flex: 1,
                  padding: 10,
                  borderRadius: 8,
                  border: "none",
                  cursor: "pointer",
                  fontWeight: 600,
                  backgroundColor: inputMode === "camera" ? "#2563eb" : "#e5e7eb",
                  color: inputMode === "camera" ? "#fff" : "#374151",
                  transition: "background-color 0.2s",
                }}
              >
                📷 カメラ読取
              </button>
            </div>

            {inputMode === "manual" ? (
              <form onSubmit={handleAddItem}>
                <label
                  htmlFor="productCode"
                  style={{ fontSize: 14, color: "#6b7280", display: "block", marginBottom: 6 }}
                >
                  商品コード
                </label>
                <div style={{ display: "flex", gap: 8 }}>
                  <input
                    id="productCode"
                    type="text"
                    value={productCode}
                    onChange={(e) => setProductCode(e.target.value)}
                    placeholder="例: 4901234567890"
                    style={{
                      flex: 1,
                      padding: "10px 12px",
                      borderRadius: 8,
                      border: "1px solid #d1d5db",
                      fontSize: 16,
                    }}
                  />
                  <button
                    type="submit"
                    style={{
                      padding: "10px 20px",
                      borderRadius: 8,
                      border: "none",
                      backgroundColor: "#2563eb",
                      color: "#fff",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    追加
                  </button>
                </div>
              </form>
            ) : (
              <div>
                <div
                  id={SCANNER_ELEMENT_ID}
                  style={{
                    width: "100%",
                    borderRadius: 8,
                    overflow: "hidden",
                    backgroundColor: "#111827",
                    minHeight: 200,
                  }}
                />
                <p style={{ fontSize: 13, color: "#6b7280", marginTop: 8 }}>
                  {isScannerReady
                    ? "バーコードをカメラに映してください(自動で読み取ります)"
                    : "カメラを起動しています..."}
                </p>
              </div>
            )}
          </div>

          {errorMessage && (
            <div
              style={{
                backgroundColor: "#fef2f2",
                color: "#b91c1c",
                padding: "10px 14px",
                borderRadius: 8,
                marginBottom: 24,
                fontSize: 14,
              }}
            >
              {errorMessage}
            </div>
          )}
        </div>

        {/* 右カラム: 商品一覧・合計 */}
        <div style={{ flex: "1.4 1 480px", minWidth: 340 }}>
          <h2 style={{ fontSize: 18, marginBottom: 12, color: "#1f2937" }}>
            購入リスト
          </h2>

          <div
            style={{
              backgroundColor: "#ffffff",
              borderRadius: 12,
              padding: preview && preview.items.length > 0 ? 0 : 20,
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              marginBottom: 24,
              overflow: "hidden",
            }}
          >
            {preview && preview.items.length > 0 ? (
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ backgroundColor: "#f9fafb" }}>
                    <th style={{ textAlign: "left", padding: "10px 14px", fontSize: 13, color: "#6b7280" }}>
                      商品名
                    </th>
                    <th style={{ textAlign: "right", padding: "10px 14px", fontSize: 13, color: "#6b7280" }}>
                      単価
                    </th>
                    <th style={{ textAlign: "right", padding: "10px 14px", fontSize: 13, color: "#6b7280" }}>
                      数量
                    </th>
                    <th style={{ textAlign: "right", padding: "10px 14px", fontSize: 13, color: "#6b7280" }}>
                      小計
                    </th>
                    <th style={{ padding: "10px 14px" }} />
                  </tr>
                </thead>
                <tbody>
                  {preview.items.map((item) => (
                    <tr key={item.product_id} style={{ borderTop: "1px solid #f3f4f6" }}>
                      <td style={{ padding: "10px 14px" }}>{item.product_name}</td>
                      <td style={{ textAlign: "right", padding: "10px 14px" }}>
                        ¥{item.unit_price}
                      </td>
                      <td style={{ textAlign: "right", padding: "10px 14px" }}>
                        {item.quantity}
                      </td>
                      <td style={{ textAlign: "right", padding: "10px 14px" }}>
                        ¥{item.subtotal_excl_tax}
                      </td>
                      <td style={{ textAlign: "right", padding: "10px 14px" }}>
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(item.product_code)}
                          style={{
                            border: "none",
                            backgroundColor: "#fee2e2",
                            color: "#b91c1c",
                            borderRadius: 6,
                            padding: "6px 10px",
                            cursor: "pointer",
                            fontSize: 13,
                          }}
                        >
                          削除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ color: "#9ca3af", textAlign: "center", margin: 0 }}>
                商品がまだ追加されていません
              </p>
            )}
          </div>

          {isLoading && (
            <p style={{ color: "#6b7280", fontSize: 14 }}>計算中...</p>
          )}

          {preview && (
            <div
              style={{
                backgroundColor: "#ffffff",
                borderRadius: 12,
                padding: 20,
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                textAlign: "right",
              }}
            >
              <p style={{ margin: "4px 0", fontSize: 14, color: "#6b7280" }}>
                税抜合計: ¥{preview.total_excl_tax}
              </p>
              <p style={{ margin: "4px 0", fontSize: 22, fontWeight: 700, color: "#1f2937" }}>
                税込合計: ¥{preview.total_incl_tax}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}