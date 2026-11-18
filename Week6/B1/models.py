from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=False)
    pwd_hash = mapped_column(String(255), nullable=False)
    # comma-separated để giữ đơn giản như claims {"roles":[...]} ở slide 16
    roles = mapped_column(String(100), default="viewer")
    scopes = mapped_column(String(200), default="orders:read")

    def roles_list(self):
        return [r for r in self.roles.split(",") if r]

    def scopes_list(self):
        return [s for s in self.scopes.split(",") if s]


class Order(db.Model):
    """Dùng cho demo ownership/BOLA (slide 24-26)."""
    __tablename__ = "orders"
    id = mapped_column(Integer, primary_key=True)
    item = mapped_column(String(200), nullable=False)
    amount = mapped_column(Integer, nullable=False)
    owner_id = mapped_column(ForeignKey("users.id"), nullable=False)

    def to_dict(self):
        return {"id": f"o-{self.id:03d}", "item": self.item,
                "amount": self.amount, "owner_id": self.owner_id}


class ApiKey(db.Model):
    """Schema rút gọn từ slide 10 (bỏ ip_allowlist/expires_at cho gọn demo)."""
    __tablename__ = "api_keys"
    id = mapped_column(Integer, primary_key=True)
    prefix = mapped_column(String(16), nullable=False)
    hash = mapped_column(String(64), nullable=False)       # sha256(key)
    last4 = mapped_column(String(4), nullable=False)
    owner_id = mapped_column(ForeignKey("users.id"), nullable=False)
    scopes = mapped_column(String(200), default="orders:read")
    revoked_at = mapped_column(DateTime, nullable=True)
