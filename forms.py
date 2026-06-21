from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegisterForm(FlaskForm):
    username = StringField("ชื่อผู้ใช้", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("อีเมล", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("รหัสผ่าน", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "ยืนยันรหัสผ่าน",
        validators=[DataRequired(), EqualTo("password", message="รหัสผ่านไม่ตรงกัน")],
    )
    submit = SubmitField("สมัครสมาชิก")


class LoginForm(FlaskForm):
    username = StringField("ชื่อผู้ใช้", validators=[DataRequired()])
    password = PasswordField("รหัสผ่าน", validators=[DataRequired()])
    submit = SubmitField("เข้าสู่ระบบ")


class ExpenseForm(FlaskForm):
    restaurant_id = SelectField("ร้านอาหาร", coerce=int, validators=[DataRequired()])
    menu_id = SelectField("เมนู", coerce=int, validators=[DataRequired()])
    price = FloatField("ราคา", validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField(
        "หมวดหมู่",
        choices=[
            ("อาหาร", "อาหาร"),
            ("เครื่องดื่ม", "เครื่องดื่ม"),
            ("ของว่าง", "ของว่าง"),
            ("สั่งของออนไลน์", "สั่งของออนไลน์"),
        ],
        validators=[DataRequired()],
    )
    expense_date = DateField("วันที่", default=date.today, validators=[DataRequired()])
    note = StringField("หมายเหตุ / โน้ตเพิ่มเติม", validators=[Optional(), Length(max=200)])
    submit = SubmitField("บันทึก")


class BudgetForm(FlaskForm):
    daily_budget = FloatField(
        "งบรายวัน",
        validators=[Optional(), NumberRange(min=0, message="งบต้องไม่ติดลบ")],
    )
    submit = SubmitField("บันทึกงบประมาณ")


class ProfileForm(FlaskForm):
    email = StringField("อีเมล", validators=[DataRequired(), Email(), Length(max=120)])
    old_password = PasswordField("รหัสผ่านปัจจุบัน (เพื่อยืนยันการเปลี่ยนแปลง)", validators=[DataRequired()])
    new_password = PasswordField("รหัสผ่านใหม่ (เว้นว่างไว้หากไม่ต้องการเปลี่ยน)", validators=[Optional(), Length(min=6)])
    confirm_new_password = PasswordField(
        "ยืนยันรหัสผ่านใหม่",
        validators=[Optional(), EqualTo("new_password", message="รหัสผ่านใหม่ไม่ตรงกัน")]
    )
    submit = SubmitField("บันทึกการเปลี่ยนแปลง")


class OnlineOrderForm(FlaskForm):
    platform = SelectField(
        "แพลตฟอร์ม / ช่องทาง",
        choices=[
            ("Shopee", "Shopee"),
            ("Lazada", "Lazada"),
            ("TikTok Shop", "TikTok Shop"),
            ("Grab", "Grab"),
            ("Lineman", "Lineman"),
            ("Foodpanda", "Foodpanda"),
            ("TikTok", "TikTok"),
            ("Facebook", "Facebook"),
            ("Instagram", "Instagram"),
            ("อื่นๆ", "อื่นๆ"),
        ],
        validators=[DataRequired()],
    )
    store_name = StringField("ชื่อร้านค้า", validators=[DataRequired(), Length(max=100)])
    item_name = StringField("ชื่อสินค้า / รายการ", validators=[DataRequired(), Length(max=100)])
    price = FloatField("ราคาสินค้า (บาท)", validators=[DataRequired(), NumberRange(min=0)])
    shipping_cost = FloatField("ค่าจัดส่ง (บาท)", default=0.0, validators=[Optional(), NumberRange(min=0)])
    status = SelectField(
        "สถานะการสั่งซื้อ",
        choices=[
            ("สั่งซื้อแล้ว", "สั่งซื้อแล้ว"),
            ("กำลังจัดส่ง", "กำลังจัดส่ง"),
            ("ได้รับแล้ว", "ได้รับแล้ว"),
            ("ยกเลิก", "ยกเลิก"),
        ],
        default="สั่งซื้อแล้ว",
        validators=[DataRequired()],
    )
    order_date = DateField("วันที่สั่งซื้อ", default=date.today, validators=[DataRequired()])
    tracking_number = StringField("เลขพัสดุ (Tracking Number)", validators=[Optional(), Length(max=100)])
    note = StringField("หมายเหตุ / โน้ตเพิ่มเติม", validators=[Optional(), Length(max=200)])
    submit = SubmitField("บันทึกรายการสั่งซื้อ")


