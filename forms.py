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
    expense_date = DateField("วันที่", default=date.today, validators=[DataRequired()])
    submit = SubmitField("บันทึก")


class BudgetForm(FlaskForm):
    daily_budget = FloatField(
        "งบรายวัน",
        validators=[Optional(), NumberRange(min=0, message="งบต้องไม่ติดลบ")],
    )
    submit = SubmitField("บันทึกงบประมาณ")
