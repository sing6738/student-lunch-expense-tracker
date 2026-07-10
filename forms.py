from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


def strip_filter(value):
    """ฟังก์ชันตัดช่องว่างหัวท้ายสำหรับฟิลด์ข้อความ"""
    return value.strip() if value else value


class RegisterForm(FlaskForm):
    username = StringField(
        "ชื่อผู้ใช้",
        filters=[strip_filter],
        validators=[
            DataRequired(message="กรุณากรอกชื่อผู้ใช้"),
            Length(min=3, max=80, message="ชื่อผู้ใช้ต้องมีความยาวระหว่าง 3 ถึง 80 ตัวอักษร")
        ]
    )
    email = StringField(
        "อีเมล",
        filters=[strip_filter],
        validators=[
            DataRequired(message="กรุณากรอกอีเมล"),
            Email(message="รูปแบบอีเมลไม่ถูกต้อง"),
            Length(max=120, message="อีเมลยาวเกินไป (สูงสุด 120 ตัวอักษร)")
        ]
    )
    password = PasswordField(
        "รหัสผ่าน",
        validators=[
            DataRequired(message="กรุณากรอกรหัสผ่าน"),
            Length(min=6, message="รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
        ]
    )
    confirm_password = PasswordField(
        "ยืนยันรหัสผ่าน",
        validators=[
            DataRequired(message="กรุณายืนยันรหัสผ่าน"),
            EqualTo("password", message="รหัสผ่านไม่ตรงกัน")
        ]
    )
    submit = SubmitField("สมัครสมาชิก")


class LoginForm(FlaskForm):
    username = StringField(
        "ชื่อผู้ใช้",
        filters=[strip_filter],
        validators=[DataRequired(message="กรุณากรอกชื่อผู้ใช้")]
    )
    password = PasswordField(
        "รหัสผ่าน",
        validators=[DataRequired(message="กรุณากรอกรหัสผ่าน")]
    )
    submit = SubmitField("เข้าสู่ระบบ")


class ExpenseForm(FlaskForm):
    restaurant_id = SelectField(
        "ร้านอาหาร",
        coerce=int,
        validators=[DataRequired(message="กรุณาเลือกร้านอาหาร")]
    )
    menu_id = SelectField(
        "เมนู",
        coerce=int,
        validators=[DataRequired(message="กรุณาเลือกเมนู")]
    )
    price = FloatField(
        "ราคา",
        validators=[
            DataRequired(message="กรุณากรอกราคา"),
            NumberRange(min=0, message="ราคาต้องไม่ต่ำกว่า 0 บาท")
        ]
    )
    category = SelectField(
        "หมวดหมู่",
        choices=[
            ("อาหาร", "อาหาร"),
            ("เครื่องดื่ม", "เครื่องดื่ม"),
            ("ของว่าง", "ของว่าง"),
            ("สั่งของออนไลน์", "สั่งของออนไลน์"),
        ],
        validators=[DataRequired(message="กรุณาเลือกหมวดหมู่")]
    )
    expense_date = DateField(
        "วันที่",
        default=date.today,
        validators=[DataRequired(message="กรุณากรอกวันที่")]
    )
    note = StringField(
        "หมายเหตุ / โน้ตเพิ่มเติม",
        filters=[strip_filter],
        validators=[
            Optional(),
            Length(max=200, message="หมายเหตุยาวเกินไป (สูงสุด 200 ตัวอักษร)")
        ]
    )
    submit = SubmitField("บันทึก")


class BudgetForm(FlaskForm):
    daily_budget = FloatField(
        "งบรายวัน",
        validators=[
            Optional(),
            NumberRange(min=0, message="งบต้องไม่ติดลบ")
        ]
    )
    submit = SubmitField("บันทึกงบประมาณ")


class ProfileForm(FlaskForm):
    email = StringField(
        "อีเมล",
        filters=[strip_filter],
        validators=[
            DataRequired(message="กรุณากรอกอีเมล"),
            Email(message="รูปแบบอีเมลไม่ถูกต้อง"),
            Length(max=120, message="อีเมลยาวเกินไป (สูงสุด 120 ตัวอักษร)")
        ]
    )
    old_password = PasswordField(
        "รหัสผ่านปัจจุบัน (เพื่อยืนยันการเปลี่ยนแปลง)",
        validators=[DataRequired(message="กรุณากรอกรหัสผ่านปัจจุบัน")]
    )
    new_password = PasswordField(
        "รหัสผ่านใหม่ (เว้นว่างไว้หากไม่ต้องการเปลี่ยน)",
        validators=[
            Optional(),
            Length(min=6, message="รหัสผ่านใหม่ต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
        ]
    )
    confirm_new_password = PasswordField(
        "ยืนยันรหัสผ่านใหม่",
        validators=[
            Optional(),
            EqualTo("new_password", message="รหัสผ่านใหม่ไม่ตรงกัน")
        ]
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
        validators=[DataRequired(message="กรุณาเลือกช่องทาง")]
    )
    store_name = StringField(
        "ชื่อร้านค้า",
        filters=[strip_filter],
        validators=[
            DataRequired(message="กรุณากรอกชื่อร้านค้า"),
            Length(max=100, message="ชื่อร้านค้าต้องไม่เกิน 100 ตัวอักษร")
        ]
    )
    item_name = StringField(
        "ชื่อสินค้า / รายการ",
        filters=[strip_filter],
        validators=[
            DataRequired(message="กรุณากรอกชื่อสินค้า"),
            Length(max=100, message="ชื่อสินค้าต้องไม่เกิน 100 ตัวอักษร")
        ]
    )
    price = FloatField(
        "ราคาสินค้า (บาท)",
        validators=[
            DataRequired(message="กรุณากรอกราคาสินค้า"),
            NumberRange(min=0, message="ราคาต้องไม่ต่ำกว่า 0 บาท")
        ]
    )
    shipping_cost = FloatField(
        "ค่าจัดส่ง (บาท)",
        default=0.0,
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าจัดส่งต้องไม่ต่ำกว่า 0 บาท")
        ]
    )
    status = SelectField(
        "สถานะการสั่งซื้อ",
        choices=[
            ("สั่งซื้อแล้ว", "สั่งซื้อแล้ว"),
            ("กำลังจัดส่ง", "กำลังจัดส่ง"),
            ("ได้รับแล้ว", "ได้รับแล้ว"),
            ("ยกเลิก", "ยกเลิก"),
        ],
        default="สั่งซื้อแล้ว",
        validators=[DataRequired(message="กรุณาเลือกสถานะ")]
    )
    order_date = DateField(
        "วันที่สั่งซื้อ",
        default=date.today,
        validators=[DataRequired(message="กรุณากรอกวันที่สั่งซื้อ")]
    )
    tracking_number = StringField(
        "เลขพัสดุ (Tracking Number)",
        filters=[strip_filter],
        validators=[
            Optional(),
            Length(max=100, message="เลขพัสดุยาวเกินไป (สูงสุด 100 ตัวอักษร)")
        ]
    )
    note = StringField(
        "หมายเหตุ / โน้ตเพิ่มเติม",
        filters=[strip_filter],
        validators=[
            Optional(),
            Length(max=200, message="หมายเหตุยาวเกินไป (สูงสุด 200 ตัวอักษร)")
        ]
    )
    submit = SubmitField("บันทึกรายการสั่งซื้อ")


class MonthlyBudgetForm(FlaskForm):
    """ฟอร์มตั้งงบประมาณรายเดือน + ค่าใช้จ่ายคงที่"""
    monthly_income = FloatField(
        "รายรับ / งบรายเดือนทั้งหมด (บาท)",
        validators=[
            DataRequired(message="กรุณากรอกรายรับ"),
            NumberRange(min=0, message="รายรับต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_internet = FloatField(
        "ค่าอินเทอร์เน็ต",
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าบริการต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_phone = FloatField(
        "ค่าโทรศัพท์",
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าบริการต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_water = FloatField(
        "ค่าน้ำ",
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าบริการต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_electric = FloatField(
        "ค่าไฟ",
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าบริการต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_rent = FloatField(
        "ค่าเช่า / ค่าหอพัก",
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าเช่าต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_other = FloatField(
        "ค่าใช้จ่ายคงที่อื่นๆ",
        validators=[
            Optional(),
            NumberRange(min=0, message="ค่าใช้จ่ายต้องไม่ติดลบ")
        ],
        default=0.0,
    )
    fixed_other_note = StringField(
        "หมายเหตุ (อื่นๆ)",
        filters=[strip_filter],
        validators=[
            Optional(),
            Length(max=200, message="หมายเหตุยาวเกินไป (สูงสุด 200 ตัวอักษร)")
        ]
    )
    submit = SubmitField("บันทึกงบประมาณ")
