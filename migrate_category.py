"""Migration script: เพิ่ม column 'category' ใน table 'expense'

รันครั้งเดียว:  python migrate_category.py
ข้อมูลเดิมจะได้ค่า default = 'อาหาร'
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ตรวจว่า column มีอยู่แล้วหรือยัง
    cursor.execute("PRAGMA table_info(expense)")
    columns = [row[1] for row in cursor.fetchall()]

    if "category" in columns:
        print("[OK] column 'category' มีอยู่แล้ว — ไม่ต้อง migrate")
    else:
        cursor.execute(
            "ALTER TABLE expense ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT 'อาหาร'"
        )
        conn.commit()
        print("[OK] เพิ่ม column 'category' สำเร็จ (default = 'อาหาร')")

    conn.close()


if __name__ == "__main__":
    migrate()
