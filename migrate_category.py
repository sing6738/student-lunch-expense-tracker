import os
from sqlalchemy import text, inspect
from app import create_app
from models import db


def migrate():
    app = create_app()
    with app.app_context():
        # ตรวจสอบโครงสร้างตารางด้วย SQLAlchemy Inspector (รองรับทั้ง SQLite และ PostgreSQL)
        inspector = inspect(db.engine)
        columns = [col["name"] for col in inspector.get_columns("expense")]

        if "category" in columns:
            print("[OK] column 'category' มีอยู่แล้ว — ไม่ต้อง migrate")
        else:
            with db.engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE expense ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT 'อาหาร'"
                    )
                )
            print("[OK] เพิ่ม column 'category' สำเร็จ (default = 'อาหาร')")

        if "note" in columns:
            print("[OK] column 'note' มีอยู่แล้ว — ไม่ต้อง migrate")
        else:
            with db.engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE expense ADD COLUMN note VARCHAR(200) NULL"
                    )
                )
            print("[OK] เพิ่ม column 'note' สำเร็จ")

        # ตรวจสอบโครงสร้างตาราง user สำหรับ wishlist_name และ wishlist_price
        user_columns = [col["name"] for col in inspector.get_columns("user")]

        if "wishlist_name" in user_columns:
            print("[OK] column 'wishlist_name' มีอยู่แล้ว — ไม่ต้อง migrate")
        else:
            try:
                with db.engine.begin() as conn:
                    conn.execute(
                        text(
                            "ALTER TABLE user ADD COLUMN wishlist_name VARCHAR(100);"
                        )
                    )
                print("[OK] เพิ่ม column 'wishlist_name' สำเร็จ")
            except Exception as e:
                print(f"[Warning] ไม่สามารถเพิ่ม column 'wishlist_name' ได้: {e}")

        if "wishlist_price" in user_columns:
            print("[OK] column 'wishlist_price' มีอยู่แล้ว — ไม่ต้อง migrate")
        else:
            try:
                with db.engine.begin() as conn:
                    conn.execute(
                        text(
                            "ALTER TABLE user ADD COLUMN wishlist_price FLOAT;"
                        )
                    )
                print("[OK] เพิ่ม column 'wishlist_price' สำเร็จ")
            except Exception as e:
                print(f"[Warning] ไม่สามารถเพิ่ม column 'wishlist_price' ได้: {e}")


if __name__ == "__main__":
    migrate()
