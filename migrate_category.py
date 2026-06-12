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


if __name__ == "__main__":
    migrate()
