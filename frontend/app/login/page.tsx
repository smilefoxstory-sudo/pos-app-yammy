"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/app/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [staffCode, setStaffCode] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!staffCode.trim() || !password.trim()) {
      setErrorMessage("スタッフコードとパスワードを入力してください");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const result = await login(staffCode, password);
      localStorage.setItem("access_token", result.access_token);
      router.push("/pos");
    } catch (err) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("予期しないエラーが発生しました");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f3f4f6",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 380,
          backgroundColor: "#ffffff",
          borderRadius: 16,
          padding: 32,
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🛒</div>
          <h1 style={{ fontSize: 24, color: "#1f2937", margin: 0 }}>
            POSレジ ログイン
          </h1>
          <p style={{ fontSize: 13, color: "#6b7280", marginTop: 6 }}>
            スタッフコードとパスワードを入力してください
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label
              htmlFor="staffCode"
              style={{ fontSize: 14, color: "#374151", display: "block", marginBottom: 6 }}
            >
              スタッフコード
            </label>
            <input
              id="staffCode"
              type="text"
              value={staffCode}
              onChange={(e) => setStaffCode(e.target.value)}
              placeholder="例: S001"
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid #d1d5db",
                fontSize: 16,
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label
              htmlFor="password"
              style={{ fontSize: 14, color: "#374151", display: "block", marginBottom: 6 }}
            >
              パスワード
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid #d1d5db",
                fontSize: 16,
                boxSizing: "border-box",
              }}
            />
          </div>

          {errorMessage && (
            <div
              style={{
                backgroundColor: "#fef2f2",
                color: "#b91c1c",
                padding: "10px 14px",
                borderRadius: 8,
                marginBottom: 16,
                fontSize: 14,
              }}
            >
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: "100%",
              padding: 12,
              borderRadius: 8,
              border: "none",
              backgroundColor: isLoading ? "#93c5fd" : "#2563eb",
              color: "#fff",
              fontWeight: 600,
              fontSize: 16,
              cursor: isLoading ? "not-allowed" : "pointer",
              transition: "background-color 0.2s",
            }}
          >
            {isLoading ? "ログイン中..." : "ログイン"}
          </button>
        </form>
      </div>
    </div>
  );
}