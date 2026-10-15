# ベースイメージとして軽量なPythonを使用
FROM python:3.11-slim

# 作業ディレクトリを指定
WORKDIR /app

# システムの依存関係が必要な場合はここでインストール（例: curlやビルドツール等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# コンテナが外部に公開するポート（Azure Container Appsなどで使用）
EXPOSE 8000

# アプリケーションの起動コマンド
# ※ main.py が backend/ 直下にある場合の例
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]