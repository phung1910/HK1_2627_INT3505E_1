import bcrypt

# bcrypt dùng chung cho Basic Auth (slide 7) và JWT login (slide 16).


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode(), stored_hash.encode())
