"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const router = useRouter();
  const [status, setStatus] = useState<string>("読み込み中...");

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setStatus(data.status);
        router.push("/login");
      })
      .catch((err) => {
        console.error(err);
        setStatus("エラーが発生しました");
      });
  }, [router]);

  return (
    <div>
      <h1>APIステータス確認</h1>
      <p>status: {status}</p>
    </div>
  );
}