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
    wishlist_name = db.Column(db.String(100), nullable=True)
    wishlist_price = db.Column(db.Float, nullable=True)
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


EXPENSE_CATEGORIES = ["อาหาร", "เครื่องดื่ม", "ของว่าง", "สั่งของออนไลน์"]


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


class OnlineOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(30), nullable=False, default="สั่งซื้อแล้ว")
    order_date = db.Column(db.Date, default=date.today, nullable=False)
    tracking_number = db.Column(db.String(100), nullable=True)
    note = db.Column(db.String(200), nullable=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expense.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("online_orders", cascade="all, delete-orphan"))
    expense = db.relationship("Expense", backref=db.backref("online_order", uselist=False))


# =========================================================
# MonthlyBudget — งบประมาณรายเดือน + ค่าใช้จ่ายคงที่
# =========================================================
class MonthlyBudget(db.Model):
    """
    บันทึกงบประมาณรายเดือนและค่าใช้จ่ายคงที่ของแต่ละเดือน
    """
    __tablename__ = "monthly_budget"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1–12

    # งบรายเดือนที่ได้รับ (รายรับ)
    monthly_income = db.Column(db.Float, nullable=False, default=0.0)

    # ค่าใช้จ่ายคงที่รายเดือน
    fixed_internet = db.Column(db.Float, nullable=False, default=0.0, comment="ค่าอินเทอร์เน็ต")
    fixed_phone = db.Column(db.Float, nullable=False, default=0.0, comment="ค่าโทรศัพท์")
    fixed_water = db.Column(db.Float, nullable=False, default=0.0, comment="ค่าน้ำ")
    fixed_electric = db.Column(db.Float, nullable=False, default=0.0, comment="ค่าไฟ")
    fixed_rent = db.Column(db.Float, nullable=False, default=0.0, comment="ค่าเช่า")
    fixed_other = db.Column(db.Float, nullable=False, default=0.0, comment="ค่าใช้จ่ายคงที่อื่นๆ")
    fixed_other_note = db.Column(db.String(200), nullable=True, comment="หมายเหตุค่าใช้จ่ายอื่นๆ")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("monthly_budgets", cascade="all, delete-orphan"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "year", "month", name="uq_user_year_month"),
    )

    @property
    def total_fixed(self):
        """รวมค่าใช้จ่ายคงที่ทั้งหมด"""
        return (
            self.fixed_internet
            + self.fixed_phone
            + self.fixed_water
            + self.fixed_electric
            + self.fixed_rent
            + self.fixed_other
        )

    @property
    def remaining_for_variable(self):
        """เงินที่เหลือหลังหักค่าใช้จ่ายคงที่ (ใช้ซื้ออาหาร ฯลฯ)"""
        return max(self.monthly_income - self.total_fixed, 0)
