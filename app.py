import csv
import io
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf import CSRFProtect
from sqlalchemy import extract, func

from config import Config
from forms import BudgetForm, ExpenseForm, LoginForm, RegisterForm, ProfileForm
from models import EXPENSE_CATEGORIES, Expense, Menu, Restaurant, User, db


csrf = CSRFProtect()

MENU_SEED = {
    "ข้าวราดแกง": [
        ("ธรรมดา", 30),
        ("เพิ่มไข่", 35),
        ("พิเศษ", 40),
        ("พิเศษ + ไข่", 45),
    ],
    "ก๋วยเตี๋ยว": [
        ("ธรรมดา", 30),
        ("พิเศษ", 35),
        ("พิเศษมาก", 40),
    ],
    "เครื่องดื่ม": [
        ("น้ำเปล่า", 5),
        ("น้ำสิงค์", 7),
        ("ชาเย็น", 20),
        ("โกโก้", 25),
    ],
    "ของทอด": [
        ("ไก่ทอด", 25),
        ("ลูกชิ้นทอด", 20),
        ("เฟรนช์ฟรายส์", 30),
    ],
    "อื่นๆ": [
        ("ขนม", 15),
        ("ผลไม้", 10),
        ("กำหนดเอง", 0),
    ],
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()
        seed_restaurants_and_menus()

    register_template_filters(app)
    register_error_handlers(app)
    register_routes(app)
    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def seed_restaurants_and_menus():
    for restaurant_name, menus in MENU_SEED.items():
        restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
        if restaurant is None:
            restaurant = Restaurant(name=restaurant_name)
            db.session.add(restaurant)
            db.session.flush()

        existing = {menu.menu_name for menu in restaurant.menus}
        for menu_name, price in menus:
            if menu_name not in existing:
                db.session.add(Menu(restaurant=restaurant, menu_name=menu_name, price=price))
    db.session.commit()


def register_template_filters(app):
    @app.template_filter("baht")
    def baht(value):
        return f"{float(value or 0):,.2f}"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("กรุณาเข้าสู่ระบบก่อนใช้งาน", "warning")
            return redirect(url_for("login", next=request.path))
        if current_user() is None:
            session.clear()
            flash("Session หมดอายุ กรุณาเข้าสู่ระบบใหม่", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def populate_expense_form_choices(form):
    restaurants = Restaurant.query.order_by(Restaurant.name.asc()).all()
    form.restaurant_id.choices = [(restaurant.id, restaurant.name) for restaurant in restaurants]

    selected_restaurant_id = form.restaurant_id.data or (restaurants[0].id if restaurants else 0)
    menus = Menu.query.filter_by(restaurant_id=selected_restaurant_id).order_by(Menu.menu_name.asc()).all()
    form.menu_id.choices = [(menu.id, menu.menu_name) for menu in menus]


def get_menu_payload():
    restaurants = Restaurant.query.order_by(Restaurant.name.asc()).all()
    return {
        str(restaurant.id): [
            {"id": menu.id, "name": menu.menu_name, "price": menu.price}
            for menu in sorted(restaurant.menus, key=lambda item: item.menu_name)
        ]
        for restaurant in restaurants
    }


def user_expenses_query(user_id):
    return (
        Expense.query.filter_by(user_id=user_id)
        .join(Menu)
        .join(Restaurant)
    )


def period_total(user_id, start_date, end_date):
    return (
        db.session.query(func.coalesce(func.sum(Expense.price), 0))
        .filter(
            Expense.user_id == user_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        )
        .scalar()
    )


def dashboard_chart_data(user_id):
    today = date.today()
    start = today - timedelta(days=6)
    rows = (
        db.session.query(Expense.expense_date, func.sum(Expense.price))
        .filter(Expense.user_id == user_id, Expense.expense_date >= start)
        .group_by(Expense.expense_date)
        .order_by(Expense.expense_date.asc())
        .all()
    )
    totals = {row[0]: float(row[1]) for row in rows}
    labels = []
    values = []
    for offset in range(7):
        day = start + timedelta(days=offset)
        labels.append(day.strftime("%d/%m"))
        values.append(totals.get(day, 0))
    return {"labels": labels, "values": values}


def analytics_payload(user_id):
    today = date.today()
    monthly_rows = (
        db.session.query(
            extract("year", Expense.expense_date).label("year"),
            extract("month", Expense.expense_date).label("month"),
            func.sum(Expense.price),
        )
        .filter(Expense.user_id == user_id)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    restaurant_rows = (
        db.session.query(Restaurant.name, func.count(Expense.id), func.sum(Expense.price))
        .join(Menu, Menu.restaurant_id == Restaurant.id)
        .join(Expense, Expense.menu_id == Menu.id)
        .filter(Expense.user_id == user_id)
        .group_by(Restaurant.id)
        .order_by(func.count(Expense.id).desc())
        .all()
    )
    menu_rows = (
        db.session.query(Menu.menu_name, func.count(Expense.id))
        .join(Expense, Expense.menu_id == Menu.id)
        .filter(Expense.user_id == user_id)
        .group_by(Menu.id)
        .order_by(func.count(Expense.id).desc())
        .all()
    )

    day_count = (
        db.session.query(func.count(func.distinct(Expense.expense_date)))
        .filter(Expense.user_id == user_id)
        .scalar()
    )
    total_spent = (
        db.session.query(func.coalesce(func.sum(Expense.price), 0))
        .filter(Expense.user_id == user_id)
        .scalar()
    )

    daily_rows = (
        db.session.query(Expense.expense_date, func.sum(Expense.price))
        .filter(Expense.user_id == user_id)
        .group_by(Expense.expense_date)
        .order_by(Expense.expense_date.desc())
        .limit(30)
        .all()
    )
    daily_rows.reverse() # Show in chronological order (oldest to newest)

    monthly_labels = [f"{int(month):02d}/{int(year)}" for year, month, _ in monthly_rows]
    monthly_values = [float(total) for _, _, total in monthly_rows]

    return {
        "favorite_restaurant": restaurant_rows[0][0] if restaurant_rows else "-",
        "favorite_menu": menu_rows[0][0] if menu_rows else "-",
        "average_per_day": float(total_spent / day_count) if day_count else 0,
        "monthly_total": period_total(user_id, today.replace(day=1), today),
        "pie": {
            "labels": [row[0] for row in restaurant_rows],
            "values": [float(row[2] or 0) for row in restaurant_rows],
        },
        "bar": {"labels": monthly_labels, "values": monthly_values},
        "line": {
            "labels": [row[0].strftime("%d/%m") for row in daily_rows],
            "values": [float(row[1] or 0) for row in daily_rows],
        },
    }


def register_routes(app):
    @app.context_processor
    def inject_user():
        return {"current_user": current_user()}

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            username_exists = User.query.filter_by(username=form.username.data.strip()).first()
            email_exists = User.query.filter_by(email=form.email.data.strip().lower()).first()
            if username_exists:
                flash("ชื่อผู้ใช้นี้ถูกใช้งานแล้ว", "danger")
            elif email_exists:
                flash("อีเมลนี้ถูกใช้งานแล้ว", "danger")
            else:
                user = User(
                    username=form.username.data.strip(),
                    email=form.email.data.strip().lower(),
                )
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ", "success")
                return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.strip()).first()
            if user and user.check_password(form.password.data):
                session.clear()
                session["user_id"] = user.id
                session["username"] = user.username
                flash("เข้าสู่ระบบสำเร็จ", "success")
                return redirect(request.args.get("next") or url_for("dashboard"))
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    def logout():
        session.clear()
        flash("ออกจากระบบแล้ว", "info")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        today_total = period_total(user.id, today, today)
        week_total = period_total(user.id, week_start, today)
        month_total = period_total(user.id, month_start, today)
        latest_expenses = (
            Expense.query.filter_by(user_id=user.id)
            .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
            .limit(10)
            .all()
        )
        over_budget = user.daily_budget is not None and today_total > user.daily_budget

        # Monthly budget progress
        import calendar
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        monthly_budget = (user.daily_budget * days_in_month) if user.daily_budget else None
        budget_percent = min(round(float(month_total) / float(monthly_budget) * 100, 1), 100) if monthly_budget else None

        return render_template(
            "dashboard.html",
            today_total=today_total,
            week_total=week_total,
            month_total=month_total,
            latest_expenses=latest_expenses,
            chart_data=dashboard_chart_data(user.id),
            over_budget=over_budget,
            monthly_budget=monthly_budget,
            budget_percent=budget_percent,
        )

    @app.route("/expenses/add", methods=["GET", "POST"])
    @login_required
    def add_expense():
        form = ExpenseForm()
        if request.method == "POST":
            form.restaurant_id.data = int(request.form.get("restaurant_id", 0))
        populate_expense_form_choices(form)
        if form.validate_on_submit():
            menu = db.session.get(Menu, form.menu_id.data)
            if menu is None or menu.restaurant_id != form.restaurant_id.data:
                flash("ข้อมูลเมนูไม่ถูกต้อง", "danger")
            else:
                expense = Expense(
                    user_id=session["user_id"],
                    menu_id=menu.id,
                    price=form.price.data,
                    category=form.category.data,
                    note=form.note.data.strip() if form.note.data else None,
                    expense_date=form.expense_date.data,
                )
                db.session.add(expense)
                db.session.commit()
                flash("บันทึกรายการอาหารแล้ว", "success")
                return redirect(url_for("dashboard"))
        return render_template("add_expense.html", form=form, menus_by_restaurant=get_menu_payload())

    @app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_expense(expense_id):
        expense = Expense.query.filter_by(id=expense_id, user_id=session["user_id"]).first_or_404()
        form = ExpenseForm(obj=expense)
        if request.method == "GET":
            form.restaurant_id.data = expense.menu.restaurant_id
            form.menu_id.data = expense.menu_id
        elif request.method == "POST":
            form.restaurant_id.data = int(request.form.get("restaurant_id", 0))
        populate_expense_form_choices(form)
        if form.validate_on_submit():
            menu = db.session.get(Menu, form.menu_id.data)
            if menu is None or menu.restaurant_id != form.restaurant_id.data:
                flash("ข้อมูลเมนูไม่ถูกต้อง", "danger")
            else:
                expense.menu_id = menu.id
                expense.price = form.price.data
                expense.category = form.category.data
                expense.note = form.note.data.strip() if form.note.data else None
                expense.expense_date = form.expense_date.data
                db.session.commit()
                flash("แก้ไขรายการแล้ว", "success")
                return redirect(url_for("history"))
        return render_template("add_expense.html", form=form, menus_by_restaurant=get_menu_payload(), expense=expense)

    @app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
    @login_required
    def delete_expense(expense_id):
        expense = Expense.query.filter_by(id=expense_id, user_id=session["user_id"]).first_or_404()
        db.session.delete(expense)
        db.session.commit()
        flash("ลบรายการแล้ว", "info")
        return redirect(url_for("history"))

    @app.route("/history")
    @login_required
    def history():
        page = request.args.get("page", 1, type=int)
        search_date = request.args.get("date", "", type=str)
        restaurant_id = request.args.get("restaurant_id", 0, type=int)
        category = request.args.get("category", "", type=str)

        query = user_expenses_query(session["user_id"])
        if search_date:
            try:
                parsed_date = datetime.strptime(search_date, "%Y-%m-%d").date()
                query = query.filter(Expense.expense_date == parsed_date)
            except ValueError:
                flash("รูปแบบวันที่ไม่ถูกต้อง", "warning")
        if restaurant_id:
            query = query.filter(Restaurant.id == restaurant_id)
        if category and category in EXPENSE_CATEGORIES:
            query = query.filter(Expense.category == category)

        pagination = query.order_by(Expense.expense_date.desc(), Expense.created_at.desc()).paginate(
            page=page,
            per_page=app.config["ITEMS_PER_PAGE"],
            error_out=False,
        )
        restaurants = Restaurant.query.order_by(Restaurant.name.asc()).all()
        return render_template(
            "history.html",
            pagination=pagination,
            restaurants=restaurants,
            search_date=search_date,
            restaurant_id=restaurant_id,
            category=category,
            categories=EXPENSE_CATEGORIES,
        )

    @app.route("/history/export")
    @login_required
    def export_history():
        search_date = request.args.get("date", "", type=str)
        restaurant_id = request.args.get("restaurant_id", 0, type=int)
        category = request.args.get("category", "", type=str)

        query = user_expenses_query(session["user_id"])
        if search_date:
            try:
                parsed_date = datetime.strptime(search_date, "%Y-%m-%d").date()
                query = query.filter(Expense.expense_date == parsed_date)
            except ValueError:
                pass
        if restaurant_id:
            query = query.filter(Restaurant.id == restaurant_id)
        if category and category in EXPENSE_CATEGORIES:
            query = query.filter(Expense.category == category)

        expenses = query.order_by(Expense.expense_date.desc(), Expense.created_at.desc()).all()

        output = io.StringIO()
        output.write("\ufeff")  # BOM for Excel
        writer = csv.writer(output)
        writer.writerow(["วันที่", "ร้าน", "เมนู", "หมวดหมู่", "ราคา"])
        for exp in expenses:
            writer.writerow([
                exp.expense_date.strftime("%d/%m/%Y"),
                exp.menu.restaurant.name,
                exp.menu.menu_name,
                exp.category,
                f"{exp.price:.2f}",
            ])

        filename = f"expenses_{date.today().strftime('%Y-%m-%d')}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @app.route("/analytics")
    @login_required
    def analytics():
        data = analytics_payload(session["user_id"])
        return render_template("analytics.html", data=data)

    @app.route("/budget", methods=["GET", "POST"])
    @login_required
    def budget():
        user = current_user()
        form = BudgetForm(obj=user)
        if form.validate_on_submit():
            user.daily_budget = form.daily_budget.data
            db.session.commit()
            flash("บันทึกงบประมาณแล้ว", "success")
            return redirect(url_for("dashboard"))
        return render_template("budget.html", form=form)

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        user = current_user()
        form = ProfileForm(obj=user)
        if form.validate_on_submit():
            if not user.check_password(form.old_password.data):
                flash("รหัสผ่านปัจจุบันไม่ถูกต้อง", "danger")
            else:
                email_changed = form.email.data.strip().lower() != user.email.lower()
                if email_changed:
                    email_exists = User.query.filter(User.email == form.email.data.strip().lower(), User.id != user.id).first()
                    if email_exists:
                        flash("อีเมลนี้ถูกใช้งานแล้วโดยผู้ใช้อื่น", "danger")
                        return render_template("profile.html", form=form)
                    user.email = form.email.data.strip().lower()

                if form.new_password.data:
                    user.set_password(form.new_password.data)
                
                db.session.commit()
                flash("แก้ไขข้อมูลส่วนตัวสำเร็จ", "success")
                return redirect(url_for("profile"))
                
        total_expenses = Expense.query.filter_by(user_id=user.id).count()
        total_spent = db.session.query(func.coalesce(func.sum(Expense.price), 0)).filter(Expense.user_id == user.id).scalar()
        
        return render_template("profile.html", form=form, total_expenses=total_expenses, total_spent=total_spent, today=date.today())

    @app.route("/manage-menus")
    @login_required
    def manage_menus():
        restaurants = Restaurant.query.order_by(Restaurant.name.asc()).all()
        return render_template("manage_menu.html", restaurants=restaurants)

    @app.route("/restaurants/add", methods=["POST"])
    @login_required
    def add_restaurant():
        name = request.form.get("name", "").strip()
        if not name:
            flash("กรุณากรอกชื่อร้านอาหาร", "danger")
        else:
            existing = Restaurant.query.filter_by(name=name).first()
            if existing:
                flash("มีร้านอาหารชื่อนี้อยู่แล้ว", "danger")
            else:
                restaurant = Restaurant(name=name)
                db.session.add(restaurant)
                db.session.commit()
                flash("เพิ่มร้านอาหารสำเร็จ", "success")
        return redirect(url_for("manage_menus"))

    @app.route("/restaurants/<int:restaurant_id>/edit", methods=["POST"])
    @login_required
    def edit_restaurant(restaurant_id):
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not restaurant:
            abort(404)
        name = request.form.get("name", "").strip()
        if not name:
            flash("กรุณากรอกชื่อร้านอาหาร", "danger")
        else:
            existing = Restaurant.query.filter(Restaurant.name == name, Restaurant.id != restaurant_id).first()
            if existing:
                flash("มีร้านอาหารชื่อนี้อยู่แล้ว", "danger")
            else:
                restaurant.name = name
                db.session.commit()
                flash("แก้ไขชื่อร้านอาหารสำเร็จ", "success")
        return redirect(url_for("manage_menus"))

    @app.route("/restaurants/<int:restaurant_id>/delete", methods=["POST"])
    @login_required
    def delete_restaurant(restaurant_id):
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not restaurant:
            abort(404)
        in_use = Expense.query.join(Menu).filter(Menu.restaurant_id == restaurant_id).first()
        if in_use:
            flash("ไม่สามารถลบร้านอาหารนี้ได้ เนื่องจากมีบันทึกการใช้งานในระบบแล้ว", "danger")
        else:
            db.session.delete(restaurant)
            db.session.commit()
            flash("ลบร้านอาหารสำเร็จ", "success")
        return redirect(url_for("manage_menus"))

    @app.route("/restaurants/<int:restaurant_id>/menus/add", methods=["POST"])
    @login_required
    def add_menu(restaurant_id):
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not restaurant:
            abort(404)
        menu_name = request.form.get("menu_name", "").strip()
        price_val = request.form.get("price", "0")
        try:
            price = float(price_val)
        except ValueError:
            price = 0.0

        if not menu_name:
            flash("กรุณากรอกชื่อเมนู", "danger")
        elif price < 0:
            flash("ราคาเมนูต้องไม่ต่ำกว่า 0 บาท", "danger")
        else:
            existing = Menu.query.filter_by(restaurant_id=restaurant_id, menu_name=menu_name).first()
            if existing:
                flash("มีเมนูนี้ในร้านนี้อยู่แล้ว", "danger")
            else:
                menu = Menu(restaurant_id=restaurant_id, menu_name=menu_name, price=price)
                db.session.add(menu)
                db.session.commit()
                flash("เพิ่มเมนูสำเร็จ", "success")
        return redirect(url_for("manage_menus"))

    @app.route("/menus/<int:menu_id>/edit", methods=["POST"])
    @login_required
    def edit_menu(menu_id):
        menu = db.session.get(Menu, menu_id)
        if not menu:
            abort(404)
        menu_name = request.form.get("menu_name", "").strip()
        price_val = request.form.get("price", "0")
        try:
            price = float(price_val)
        except ValueError:
            price = 0.0

        if not menu_name:
            flash("กรุณากรอกชื่อเมนู", "danger")
        elif price < 0:
            flash("ราคาเมนูต้องไม่ต่ำกว่า 0 บาท", "danger")
        else:
            existing = Menu.query.filter(Menu.restaurant_id == menu.restaurant_id, Menu.menu_name == menu_name, Menu.id != menu_id).first()
            if existing:
                flash("มีเมนูนี้ในร้านนี้อยู่แล้ว", "danger")
            else:
                menu.menu_name = menu_name
                menu.price = price
                db.session.commit()
                flash("แก้ไขเมนูสำเร็จ", "success")
        return redirect(url_for("manage_menus"))

    @app.route("/menus/<int:menu_id>/delete", methods=["POST"])
    @login_required
    def delete_menu(menu_id):
        menu = db.session.get(Menu, menu_id)
        if not menu:
            abort(404)
        in_use = Expense.query.filter_by(menu_id=menu_id).first()
        if in_use:
            flash("ไม่สามารถลบเมนูนี้ได้ เนื่องจากมีบันทึกการใช้งานในระบบแล้ว", "danger")
        else:
            db.session.delete(menu)
            db.session.commit()
            flash("ลบเมนูสำเร็จ", "success")
        return redirect(url_for("manage_menus"))

    @app.route("/api/menus/<int:restaurant_id>")
    @login_required
    def api_menus(restaurant_id):
        restaurant = db.session.get(Restaurant, restaurant_id)
        if restaurant is None:
            abort(404)
        return jsonify(
            [
                {"id": menu.id, "name": menu.menu_name, "price": menu.price}
                for menu in restaurant.menus
            ]
        )


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
