from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    slug = mapped_column(String(100), unique=True, nullable=False)


class User(db.Model):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=False)
    display_name = mapped_column(String(100))


class Author(db.Model):
    __tablename__ = "authors"
    id = mapped_column(Integer, primary_key=True)   # slide nhắc: cần id
    name = mapped_column(String(100), nullable=False)
    bio = mapped_column(Text)
    books = relationship("Book", secondary="book_authors", back_populates="authors")


class BookAuthor(db.Model):
    """Junction có metadata (role) - 1 pair = 1 dòng"""
    __tablename__ = "book_authors"
    book_id = mapped_column(ForeignKey("books.id"), primary_key=True)
    author_id = mapped_column(ForeignKey("authors.id"), primary_key=True)
    role = mapped_column(String(10), default="co")   # lead / co / ed


class Book(db.Model):
    __tablename__ = "books"
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    isbn = mapped_column(String(13), unique=True)
    price_vnd = mapped_column(Integer, nullable=False)
    stock = mapped_column(Integer, default=0)
    category_id = mapped_column(ForeignKey("categories.id"))
    category = relationship("Category")
    authors = relationship("Author", secondary="book_authors", back_populates="books")

    def to_dict(self, fields=None):
        # Đây là API representation, KHÔNG phải ORM dump (slide 13)
        full = {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "category": {"id": self.category.id, "slug": self.category.slug}
                        if self.category else None,
            "authors": [{"id": a.id, "name": a.name} for a in self.authors],
            "price": {"amount": self.price_vnd, "currency": "VND"},
            "inStock": (self.stock or 0) > 0,
        }
        if fields is None:  # sparse fieldsets (slide 26-27)
            return full
        return {k: v for k, v in full.items() if k in fields}


class Review(db.Model):
    __tablename__ = "reviews"
    id = mapped_column(Integer, primary_key=True)
    rating = mapped_column(Integer, nullable=False)   # 1-5
    book_id = mapped_column(ForeignKey("books.id"), nullable=False)
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)