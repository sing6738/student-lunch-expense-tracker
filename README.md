# Lunch Expense App

เว็บแอปสำหรับบันทึกรายจ่ายมื้อกลางวันของนักเรียน ใช้ Flask, SQLite, SQLAlchemy, Flask-WTF, Bootstrap 5 และ Chart.js

## ฟีเจอร์หลัก

- สมัครสมาชิกและเข้าสู่ระบบด้วย session
- Hash รหัสผ่านด้วย Werkzeug
- ป้องกัน CSRF ด้วย Flask-WTF
- Dashboard แสดงยอดวันนี้ สัปดาห์นี้ เดือนนี้ รายการล่าสุด และกราฟ 7 วัน
- เพิ่ม/แก้ไข/ลบรายการอาหาร พร้อม popup ยืนยันก่อนลบ
- Dynamic menu เลือกร้านแล้วแสดงเมนูและราคาอัตโนมัติ
- ประวัติรายการพร้อมค้นหาตามวันที่ ร้านอาหาร และ pagination
- Analytics พร้อม Pie Chart, Bar Chart และ Line Chart
- ตั้งงบรายวันและแจ้งเตือนเมื่อใช้เกิน

## โครงสร้างไฟล์

```text
lunch_expense_app/
├── app.py
├── models.py
├── forms.py
├── config.py
├── requirements.txt
├── static/
│   ├── css/style.css
│   ├── js/menu.js
│   ├── js/charts.js
│   └── images/.gitkeep
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_expense.html
│   ├── history.html
│   ├── analytics.html
│   └── budget.html
└── database.db
```

`database.db` จะถูกสร้างอัตโนมัติเมื่อรันแอปครั้งแรก

## คำอธิบายส่วนสำคัญ

- `app.py` รวม Flask routes, login required decorator, seed ข้อมูลร้าน/เมนู, dashboard summary, CRUD รายจ่าย, history, analytics และ budget
- `models.py` นิยาม SQLAlchemy models: `User`, `Restaurant`, `Menu`, `Expense`
- `forms.py` นิยาม Flask-WTF forms พร้อม validation และ CSRF token
- `config.py` เก็บค่า secret key, database URL และ pagination size
- `templates/base.html` เป็น layout หลัก มี sidebar, navbar, flash messages และโหลด Bootstrap/Chart.js
- `static/js/menu.js` จัดการ dynamic menu และเติมราคาอัตโนมัติ
- `static/js/charts.js` วาดกราฟ Dashboard และ Analytics ด้วย Chart.js
- `static/css/style.css` ปรับ UI ให้ responsive และโทนสีสบายตา

## ติดตั้ง

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

บน macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## รันโปรเจกต์

```bash
flask --app app run --debug
```

จากนั้นเปิด:

```text
http://127.0.0.1:5000
```

หรือรันตรงด้วย:

```bash
python app.py
```

## หมายเหตุ Production

- เปลี่ยน `SECRET_KEY` ผ่าน environment variable ก่อน deploy
- สำหรับ production จริงควรใช้ HTTPS, secure cookie settings และ database server ที่เหมาะกับปริมาณผู้ใช้
- SQLite เหมาะกับงาน demo, prototype และระบบขนาดเล็ก
