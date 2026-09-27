# scripts/create_sample_staff.py
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def main():
  samples = [
    {"staff_code": "S001", "staff_name": "一般スタッフA", "password": "password123", "role": "general"},
    {"staff_code": "A001", "staff_name": "管理者A", "password": "adminpass456", "role": "admin"},
  ]

  for s in samples:
    hashed = password_hash.hash(s["password"])
    print(f"staff_code={s['staff_code']}, staff_name={s['staff_name']}, role={s['role']}")
    print(f"password_hash={hashed}")
    print("---")

if __name__ == "__main__":
  main()