from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import products, transactions, auth

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
  return {"status": "ok"}

app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(auth.router)