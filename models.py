from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    daily_budget = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    expenses = db.relationship("Expense", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    menus = db.relationship("Menu", back_populates="restaurant", cascade="all, delete-orphan")


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)
    menu_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    restaurant = db.relationship("Restaurant", back_populates="menus")
    expenses = db.relationship("Expense", back_populates="menu")

    __table_args__ = (
        db.UniqueConstraint("restaurant_id", "menu_name", name="uq_menu_restaurant_name"),
    )


EXPENSE_CATEGORIES = ["อาหาร", "เครื่องดื่ม", "ของว่าง"]


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False, default="อาหาร")
    note = db.Column(db.String(200), nullable=True)
    expense_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="expenses")
    menu = db.relationship("Menu", back_populates="expenses")
