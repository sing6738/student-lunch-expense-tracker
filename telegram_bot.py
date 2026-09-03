"""Long-polling Telegram bot for the Lunch Expense App.

Run as a separate process: ``python telegram_bot.py``.
The bot only accepts private chats and links each chat to an existing app account.
"""
import json
import os
import re
import time
from datetime import date
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()

from app import app
from models import Expense, Menu, Restaurant, TelegramLink, User, db


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API = f"https://api.telegram.org/bot{TOKEN}" if TOKEN else None
HELP = (
    "สวัสดีครับ ผมช่วยบันทึกค่าอาหารได้\n\n"
    "1) เชื่อมบัญชี: /link ชื่อผู้ใช้ รหัสผ่าน\n"
    "2) บันทึก: ข้าวกะเพรา 55\n"
    "3) ดูยอด: /summary\n\n"
    "คำสั่งอื่น: /help, /unlink\n"
    "กรุณาใช้ในแชตส่วนตัวกับบอทเท่านั้น"
)


def telegram(method, payload=None):
    data = urlencode(payload or {}).encode()
    request = Request(f"{API}/{method}", data=data)
    with urlopen(request, timeout=35) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API error"))
    return result["result"]


def reply(chat_id, text):
    telegram("sendMessage", {"chat_id": chat_id, "text": text})


def parse_link(text):
    parts = text.split(maxsplit=2)
    return (parts[1], parts[2]) if len(parts) == 3 else (None, None)


def default_menu():
    restaurant = Restaurant.query.filter_by(name="Telegram Bot").first()
    if not restaurant:
        restaurant = Restaurant(name="Telegram Bot")
        db.session.add(restaurant)
        db.session.flush()
    menu = Menu.query.filter_by(restaurant_id=restaurant.id, menu_name="บันทึกผ่าน Telegram").first()
    if not menu:
        menu = Menu(restaurant_id=restaurant.id, menu_name="บันทึกผ่าน Telegram", price=0)
        db.session.add(menu)
        db.session.flush()
    return menu


def handle_message(message):
    chat = message.get("chat", {})
    if chat.get("type") != "private":
        return
    chat_id = chat["id"]
    text = (message.get("text") or "").strip()
    if not text:
        reply(chat_id, "ส่งชื่อรายการและราคาได้ เช่น ข้าวมันไก่ 50")
        return

    if text.startswith("/start") or text == "/help":
        reply(chat_id, HELP)
        return
    if text == "/unlink":
        link = TelegramLink.query.filter_by(chat_id=chat_id).first()
        if link:
            db.session.delete(link)
            db.session.commit()
        reply(chat_id, "ยกเลิกการเชื่อมบัญชีแล้ว")
        return
    if text.startswith("/link"):
        username, password = parse_link(text)
        if not username or not password:
            reply(chat_id, "รูปแบบ: /link ชื่อผู้ใช้ รหัสผ่าน")
            return
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            reply(chat_id, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            return
        existing = TelegramLink.query.filter_by(chat_id=chat_id).first()
        if existing:
            db.session.delete(existing)
        old_link = TelegramLink.query.filter_by(user_id=user.id).first()
        if old_link:
            db.session.delete(old_link)
        db.session.add(TelegramLink(user_id=user.id, chat_id=chat_id))
        db.session.commit()
        reply(chat_id, f"เชื่อมกับบัญชี {user.username} สำเร็จ ลองส่ง: ข้าวกะเพรา 55")
        return

    link = TelegramLink.query.filter_by(chat_id=chat_id).first()
    if not link:
        reply(chat_id, "กรุณาเชื่อมบัญชีก่อนด้วย /link ชื่อผู้ใช้ รหัสผ่าน")
        return
    if text == "/summary":
        total = db.session.query(db.func.sum(Expense.price)).filter(
            Expense.user_id == link.user_id,
            db.extract("year", Expense.expense_date) == date.today().year,
            db.extract("month", Expense.expense_date) == date.today().month,
        ).scalar() or 0
        reply(chat_id, f"ยอดค่าอาหารเดือนนี้: {total:,.2f} บาท")
        return

    match = re.fullmatch(r"(.+?)\s+(\d+(?:\.\d{1,2})?)", text)
    if not match:
        reply(chat_id, "รูปแบบไม่ถูกต้อง ลองส่ง: ข้าวมันไก่ 50")
        return
    note, amount = match.groups()
    amount = float(amount)
    if amount <= 0:
        reply(chat_id, "ราคาต้องมากกว่า 0 บาท")
        return
    menu = default_menu()
    expense = Expense(user_id=link.user_id, menu_id=menu.id, price=amount, category="อาหาร", note=note)
    db.session.add(expense)
    db.session.commit()
    reply(chat_id, f"บันทึก {note} {amount:,.2f} บาท เรียบร้อย")


def main():
    if not TOKEN:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN. Add it to .env first.")
    offset = None
    print("Telegram bot started")
    while True:
        try:
            payload = {"timeout": 30, "allowed_updates": json.dumps(["message"])}
            if offset is not None:
                payload["offset"] = offset
            for update in telegram("getUpdates", payload):
                offset = update["update_id"] + 1
                if "message" in update:
                    with app.app_context():
                        handle_message(update["message"])
        except (URLError, RuntimeError, OSError) as error:
            print(f"Telegram error: {error}; retrying in 5 seconds")
            time.sleep(5)


if __name__ == "__main__":
    main()
