from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from functools import wraps
from models import db, User, Expense, Restaurant, Menu, MonthlyBudget, OnlineOrder

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_jwt_secret():
    from flask import current_app
    return current_app.config.get('JWT_SECRET_KEY', 'change-this-jwt-secret-in-production')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        if not token:
            return jsonify({"success": False, "error": {"code": "UNAUTHORIZED", "message": "Missing token"}}), 401
            
        try:
            data = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน"}}), 400
        
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        from flask import current_app
        expiry_hours = current_app.config.get('JWT_EXPIRY_HOURS', 24)
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
        }, get_jwt_secret(), algorithm="HS256")
        
        return jsonify({
            "success": True,
            "data": {
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "daily_budget": user.daily_budget
                }
            }
        })
        
    return jsonify({"success": False, "error": {"code": "UNAUTHORIZED", "message": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"}}), 401

@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_me(current_user):
    return jsonify({
        "success": True,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "daily_budget": current_user.daily_budget
        }
    })

@api_bp.route('/restaurants', methods=['GET'])
@token_required
def get_restaurants(current_user):
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    return jsonify({
        "success": True,
        "data": [{"id": r.id, "name": r.name, "is_active": r.is_active} for r in restaurants]
    })

@api_bp.route('/restaurants/<int:id>/menus', methods=['GET'])
@token_required
def get_menus(current_user, id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบร้านอาหาร"}}), 404
        
    return jsonify({
        "success": True,
        "data": [{"id": m.id, "restaurant_id": m.restaurant_id, "name": m.menu_name, "price": m.price, "is_active": m.is_active} for m in restaurant.menus]
    })

@api_bp.route('/expenses', methods=['GET'])
@token_required
def get_expenses(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.expense_date.desc(), Expense.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    data = []
    for e in pagination.items:
        data.append({
            "id": e.id,
            "restaurant_id": e.menu.restaurant_id if e.menu else None,
            "menu_id": e.menu_id,
            "amount": e.price,
            "category": e.category,
            "date": e.expense_date.isoformat(),
            "note": e.note,
            "restaurant": {"id": e.menu.restaurant_id, "name": e.menu.restaurant.name} if e.menu and e.menu.restaurant else None,
            "menu": {"id": e.menu_id, "name": e.menu.menu_name} if e.menu else None
        })
        
    return jsonify({
        "success": True,
        "data": data,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }
    })

@api_bp.route('/expenses', methods=['POST'])
@token_required
def create_expense(current_user):
    data = request.get_json()
    try:
        menu_id = data['menu_id']
        amount = float(data['amount'])
        category = data['category']
        expense_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        note = data.get('note', '')
        
        expense = Expense(
            user_id=current_user.id,
            menu_id=menu_id,
            price=amount,
            category=category,
            expense_date=expense_date,
            note=note
        )
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({"success": True, "data": {"id": expense.id}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

@api_bp.route('/budget', methods=['GET'])
@token_required
def get_budget(current_user):
    today = datetime.date.today()
    spent_today = db.session.query(db.func.sum(Expense.price)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date == today
    ).scalar() or 0.0
    
    return jsonify({
        "success": True,
        "data": {
            "daily_budget": current_user.daily_budget,
            "spent_today": float(spent_today),
            "remaining_today": float(current_user.daily_budget - spent_today),
            "is_over_budget": float(spent_today) > current_user.daily_budget
        }
    })


@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not password or not email:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "กรุณากรอกข้อมูลให้ครบถ้วน"}}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "ชื่อผู้ใช้นี้มีในระบบแล้ว"}}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "อีเมลนี้มีในระบบแล้ว"}}), 400
        
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"success": True, "message": "สมัครสมาชิกสำเร็จ"}), 201

@api_bp.route('/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    from flask import current_app
    expiry_hours = current_app.config.get('JWT_EXPIRY_HOURS', 24)
    token = jwt.encode({
        'user_id': current_user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
    }, get_jwt_secret(), algorithm="HS256")
    
    return jsonify({
        "success": True,
        "data": {
            "token": token
        }
    })

@api_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    # For JWT, client handles logout by destroying token. We just return success.
    return jsonify({"success": True, "message": "ออกจากระบบสำเร็จ"})

@api_bp.route('/expenses/<int:id>', methods=['GET'])
@token_required
def get_expense(current_user, id):
    e = db.session.get(Expense, id)
    if not e or e.user_id != current_user.id:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบรายการ"}}), 404
        
    return jsonify({
        "success": True,
        "data": {
            "id": e.id,
            "restaurant_id": e.menu.restaurant_id if e.menu else None,
            "menu_id": e.menu_id,
            "amount": e.price,
            "category": e.category,
            "date": e.expense_date.isoformat(),
            "note": e.note,
            "restaurant": {"id": e.menu.restaurant_id, "name": e.menu.restaurant.name} if e.menu and e.menu.restaurant else None,
            "menu": {"id": e.menu_id, "name": e.menu.menu_name} if e.menu else None
        }
    })

@api_bp.route('/expenses/<int:id>', methods=['PUT'])
@token_required
def update_expense(current_user, id):
    e = db.session.get(Expense, id)
    if not e or e.user_id != current_user.id:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบรายการ"}}), 404
        
    data = request.get_json()
    try:
        if 'menu_id' in data:
            e.menu_id = data['menu_id']
        if 'amount' in data:
            e.price = float(data['amount'])
        if 'category' in data:
            e.category = data['category']
        if 'date' in data:
            e.expense_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'note' in data:
            e.note = data.get('note', '')
            
        db.session.commit()
        return jsonify({"success": True, "data": {"id": e.id}})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(exc)}}), 400

@api_bp.route('/expenses/<int:id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, id):
    e = db.session.get(Expense, id)
    if not e or e.user_id != current_user.id:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบรายการ"}}), 404
        
    db.session.delete(e)
    db.session.commit()
    return jsonify({"success": True, "message": "ลบรายการสำเร็จ"})

@api_bp.route('/expenses/export', methods=['GET'])
@token_required
def export_expenses(current_user):
    import io, csv
    from flask import Response
    
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.expense_date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['วันที่', 'หมวดหมู่', 'ร้านอาหาร', 'เมนู', 'ราคา', 'หมายเหตุ'])
    
    for e in expenses:
        restaurant_name = e.menu.restaurant.name if e.menu and e.menu.restaurant else ''
        menu_name = e.menu.menu_name if e.menu else ''
        writer.writerow([e.expense_date.strftime('%Y-%m-%d'), e.category, restaurant_name, menu_name, e.price, e.note])
        
    return Response(
        output.getvalue().encode('utf-8-sig'),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=expenses.csv"}
    )

@api_bp.route('/menus/<int:id>', methods=['GET'])
@token_required
def get_menu(current_user, id):
    m = db.session.get(Menu, id)
    if not m:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบเมนู"}}), 404
        
    return jsonify({
        "success": True,
        "data": {
            "id": m.id,
            "restaurant_id": m.restaurant_id,
            "name": m.menu_name,
            "price": m.price,
            "restaurant": {"id": m.restaurant.id, "name": m.restaurant.name} if m.restaurant else None
        }
    })

@api_bp.route('/budget', methods=['PUT'])
@token_required
def update_budget(current_user):
    data = request.get_json()
    if 'daily_budget' in data:
        current_user.daily_budget = float(data['daily_budget'])
        db.session.commit()
        return jsonify({"success": True, "message": "อัปเดตงบประมาณสำเร็จ"})
    return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "ข้อมูลไม่ถูกต้อง"}}), 400

@api_bp.route('/analytics/summary', methods=['GET'])
@token_required
def get_analytics_summary(current_user):
    today = datetime.date.today()
    this_month = today.replace(day=1)
    
    # Today's total
    spent_today = db.session.query(db.func.sum(Expense.price)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date == today
    ).scalar() or 0.0
    
    # Month's total
    spent_month = db.session.query(db.func.sum(Expense.price)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= this_month
    ).scalar() or 0.0
    
    # Total expenses count
    expense_count = Expense.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        "success": True,
        "data": {
            "spent_today": float(spent_today),
            "spent_month": float(spent_month),
            "total_expenses": expense_count
        }
    })

@api_bp.route('/analytics/trend', methods=['GET'])
@token_required
def get_analytics_trend(current_user):
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=6)
    
    expenses = db.session.query(
        Expense.expense_date, 
        db.func.sum(Expense.price).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= seven_days_ago
    ).group_by(Expense.expense_date).all()
    
    expense_dict = {str(d): float(t) for d, t in expenses}
    
    dates = [(seven_days_ago + datetime.timedelta(days=i)).isoformat() for i in range(7)]
    data = [expense_dict.get(d, 0.0) for d in dates]
    
    return jsonify({
        "success": True,
        "data": {
            "dates": dates,
            "amounts": data
        }
    })

@api_bp.route('/analytics/categories', methods=['GET'])
@token_required
def get_analytics_categories(current_user):
    today = datetime.date.today()
    this_month = today.replace(day=1)
    
    categories = db.session.query(
        Expense.category,
        db.func.sum(Expense.price).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= this_month
    ).group_by(Expense.category).all()
    
    return jsonify({
        "success": True,
        "data": [{"category": c, "amount": float(t)} for c, t in categories]
    })

@api_bp.route('/analytics/calendar', methods=['GET'])
@token_required
def get_analytics_calendar(current_user):
    # Just return last 30 days of data
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    expenses = db.session.query(
        Expense.expense_date, 
        db.func.sum(Expense.price).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= thirty_days_ago
    ).group_by(Expense.expense_date).all()
    
    return jsonify({
        "success": True,
        "data": [{"date": str(d), "amount": float(t)} for d, t in expenses]
    })

@api_bp.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    orders = OnlineOrder.query.filter_by(user_id=current_user.id).order_by(OnlineOrder.order_date.desc()).all()
    return jsonify({
        "success": True,
        "data": [{
            "id": o.id,
            "platform": o.platform,
            "store_name": o.store_name,
            "item_name": o.item_name,
            "price": o.price,
            "shipping_cost": o.shipping_cost,
            "status": o.status,
            "order_date": o.order_date.isoformat(),
            "tracking_number": o.tracking_number,
            "note": o.note
        } for o in orders]
    })

@api_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()
    try:
        order = OnlineOrder(
            user_id=current_user.id,
            platform=data['platform'],
            store_name=data['store_name'],
            item_name=data['item_name'],
            price=float(data['price']),
            shipping_cost=float(data.get('shipping_cost', 0)),
            status=data.get('status', 'สั่งซื้อแล้ว'),
            order_date=datetime.datetime.strptime(data['date'], '%Y-%m-%d').date() if 'date' in data else datetime.date.today(),
            tracking_number=data.get('tracking_number'),
            note=data.get('note')
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": order.id}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

@api_bp.route('/orders/<int:id>', methods=['PUT'])
@token_required
def update_order(current_user, id):
    o = db.session.get(OnlineOrder, id)
    if not o or o.user_id != current_user.id:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบรายการ"}}), 404
        
    data = request.get_json()
    try:
        if 'platform' in data: o.platform = data['platform']
        if 'store_name' in data: o.store_name = data['store_name']
        if 'item_name' in data: o.item_name = data['item_name']
        if 'price' in data: o.price = float(data['price'])
        if 'shipping_cost' in data: o.shipping_cost = float(data['shipping_cost'])
        if 'status' in data: o.status = data['status']
        if 'date' in data: o.order_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'tracking_number' in data: o.tracking_number = data['tracking_number']
        if 'note' in data: o.note = data['note']
        
        db.session.commit()
        return jsonify({"success": True, "data": {"id": o.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

@api_bp.route('/orders/<int:id>', methods=['DELETE'])
@token_required
def delete_order(current_user, id):
    o = db.session.get(OnlineOrder, id)
    if not o or o.user_id != current_user.id:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ไม่พบรายการ"}}), 404
        
    db.session.delete(o)
    db.session.commit()
    return jsonify({"success": True, "message": "ลบรายการสำเร็จ"})


# --- NEW ENDPOINTS (iOS PWA Plan) ---

@api_bp.route('/expenses/batch', methods=['POST'])
@token_required
def create_expenses_batch(current_user):
    data = request.get_json()
    expenses_data = data.get('expenses', [])
    
    if not expenses_data:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "ไม่พบข้อมูลรายจ่าย"}}), 400
        
    created_ids = []
    try:
        for edata in expenses_data:
            menu_id = edata['menu_id']
            amount = float(edata['amount'])
            category = edata['category']
            expense_date = datetime.datetime.strptime(edata['date'], '%Y-%m-%d').date()
            note = edata.get('note', '')
            
            expense = Expense(
                user_id=current_user.id,
                menu_id=menu_id,
                price=amount,
                category=category,
                expense_date=expense_date,
                note=note
            )
            db.session.add(expense)
            db.session.flush() # get id
            created_ids.append(expense.id)
            
        db.session.commit()
        return jsonify({"success": True, "data": {"ids": created_ids}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

@api_bp.route('/monthly-budget', methods=['GET'])
@token_required
def get_monthly_budget(current_user):
    year = request.args.get('year', datetime.date.today().year, type=int)
    month = request.args.get('month', datetime.date.today().month, type=int)
    
    mb = MonthlyBudget.query.filter_by(user_id=current_user.id, year=year, month=month).first()
    if not mb:
        return jsonify({"success": True, "data": None})
        
    return jsonify({
        "success": True,
        "data": {
            "id": mb.id,
            "year": mb.year,
            "month": mb.month,
            "monthly_income": mb.monthly_income,
            "fixed_internet": mb.fixed_internet,
            "fixed_phone": mb.fixed_phone,
            "fixed_water": mb.fixed_water,
            "fixed_electric": mb.fixed_electric,
            "fixed_rent": mb.fixed_rent,
            "fixed_other": mb.fixed_other,
            "fixed_other_note": mb.fixed_other_note,
            "total_fixed": mb.total_fixed,
            "remaining_for_variable": mb.remaining_for_variable
        }
    })

@api_bp.route('/monthly-budget', methods=['PUT', 'POST'])
@token_required
def update_monthly_budget(current_user):
    data = request.get_json()
    year = data.get('year', datetime.date.today().year)
    month = data.get('month', datetime.date.today().month)
    
    mb = MonthlyBudget.query.filter_by(user_id=current_user.id, year=year, month=month).first()
    if not mb:
        mb = MonthlyBudget(user_id=current_user.id, year=year, month=month)
        db.session.add(mb)
        
    try:
        if 'monthly_income' in data: mb.monthly_income = float(data['monthly_income'])
        if 'fixed_internet' in data: mb.fixed_internet = float(data['fixed_internet'])
        if 'fixed_phone' in data: mb.fixed_phone = float(data['fixed_phone'])
        if 'fixed_water' in data: mb.fixed_water = float(data['fixed_water'])
        if 'fixed_electric' in data: mb.fixed_electric = float(data['fixed_electric'])
        if 'fixed_rent' in data: mb.fixed_rent = float(data['fixed_rent'])
        if 'fixed_other' in data: mb.fixed_other = float(data['fixed_other'])
        if 'fixed_other_note' in data: mb.fixed_other_note = data['fixed_other_note']
        
        db.session.commit()
        return jsonify({"success": True, "data": {"id": mb.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

@api_bp.route('/monthly-budget/summary', methods=['GET'])
@token_required
def get_monthly_budget_summary(current_user):
    year = request.args.get('year', datetime.date.today().year, type=int)
    month = request.args.get('month', datetime.date.today().month, type=int)
    
    mb = MonthlyBudget.query.filter_by(user_id=current_user.id, year=year, month=month).first()
    if not mb:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "ยังไม่ได้ตั้งค่างบประมาณเดือนนี้"}}), 404
        
    # Calculate spent in this month
    import calendar
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, last_day)
    
    spent = db.session.query(db.func.sum(Expense.price)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).scalar() or 0.0
    
    return jsonify({
        "success": True,
        "data": {
            "total_income": mb.monthly_income,
            "total_fixed": mb.total_fixed,
            "remaining_for_variable": mb.remaining_for_variable,
            "total_spent_variable": float(spent),
            "remaining_balance": mb.remaining_for_variable - float(spent)
        }
    })

@api_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "success": True,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "daily_budget": current_user.daily_budget,
            "wishlist_name": current_user.wishlist_name,
            "wishlist_price": current_user.wishlist_price
        }
    })

@api_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    try:
        if 'email' in data: current_user.email = data['email']
        if 'daily_budget' in data: current_user.daily_budget = float(data['daily_budget'])
        if 'wishlist_name' in data: current_user.wishlist_name = data['wishlist_name']
        if 'wishlist_price' in data: current_user.wishlist_price = float(data['wishlist_price']) if data['wishlist_price'] else None
        if 'password' in data and data['password']:
            current_user.set_password(data['password'])
            
        db.session.commit()
        return jsonify({"success": True, "message": "อัปเดตโปรไฟล์สำเร็จ"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400
