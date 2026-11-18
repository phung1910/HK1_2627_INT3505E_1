"""slide 27-28 — Argon2id đứng độc lập, không gắn vào app chính (app.py dùng
bcrypt cho Basic Auth + JWT login, đúng như code mẫu trong slide 7 và 16).
Chạy tay: python hash_demo.py
"""
import sys

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError

sys.stdout.reconfigure(encoding="utf-8")

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, type=Type.ID)

stored = ph.hash("example-password")
print("hash:", stored)

try:
    ph.verify(stored, "example-password")
except VerifyMismatchError:
    print("verify: MISMATCH")
else:
    print("verify: OK")
    print("needs_rehash:", ph.check_needs_rehash(stored))

try:
    ph.verify(stored, "wrong-password")
except VerifyMismatchError:
    print("verify (sai password): MISMATCH (đúng như kỳ vọng)")
