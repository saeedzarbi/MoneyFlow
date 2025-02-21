from flask import  redirect, url_for, flash, Blueprint
from jdatetime import timedelta

from extensions import bcrypt, db
from flask_login import login_user, logout_user, login_required, current_user
from persiantools.jdatetime import JalaliDate
from forms import LoginForm, ExpenseForm
from flask import render_template, request, jsonify
from datetime import datetime
from models import db, Expense, Category, User

auth_bp = Blueprint('auth', __name__)
# صفحه لاگین
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)

            return redirect(url_for('auth.dashboard'))  # هدایت به داشبورد
        else:
            flash('ورود ناموفق. لطفاً ایمیل و پسورد را بررسی کنید.', 'danger')
    return render_template('login.html', form=form)

# صفحه خروج
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # هدایت به صفحه لاگین

# صفحه داشبورد
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    return render_template('dashboard.html', categories=categories)

@auth_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    data = request.get_json()
    category_name = data.get('categoryName')

    if not category_name:
        return jsonify({'error': 'نام دسته‌بندی نمی‌تواند خالی باشد'}), 400

    existing_category = Category.query.filter_by(name=category_name).first()
    if existing_category:
        return jsonify({'error': 'این دسته‌بندی قبلاً ثبت شده است'}), 400

    new_category = Category(name=category_name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'دسته‌بندی جدید با موفقیت ثبت شد', 'category_id': new_category.id, 'category_name': new_category.name}), 201


@auth_bp.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            data = request.get_json()
            amount = data.get('amount')
            category_id = data.get('category')
            description = data.get('description')

            # بررسی صحت داده‌ها
            if not amount or not category_id:
                return jsonify({"message": "تمامی فیلدها باید پر شوند!"}), 400

            # اضافه کردن هزینه جدید به پایگاه داده
            expense = Expense(
                amount=amount,
                category_id=category_id,
                user_id=current_user.id,  # کاربری که وارد شده است
                description=description
            )
            db.session.add(expense)
            db.session.commit()

            # ارسال جواب به کاربر
            return jsonify({
                "message": "هزینه با موفقیت ثبت شد!",
                "expense": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": expense.category.name,
                    "description": expense.description,
                    "date": expense.date.strftime('%Y/%m/%d')
                }
            })

        except Exception as e:
            return jsonify({"message": "خطا در ثبت هزینه. لطفاً دوباره تلاش کنید."}), 500

@auth_bp.route('/report')
@login_required
def reports():
    return render_template('report.html')

@auth_bp.route('/get_all_report', methods=['POST'])
@login_required
def get_monthly_report():
    data = request.get_json()
    try:
        # جلب هزینه‌ها بر اساس دسته‌بندی و فیلتر بر اساس ماه
        report_data = db.session.query(
            Category.name.label('category_name'),
            db.func.sum(Expense.amount).label('total_amount')
        ).join(Expense).filter(
            Expense.user_id == current_user.id
        ).group_by(Category.id).all()

        if not report_data:
            return jsonify({"success": False, "message": "هیچ گزارشی برای این ماه موجود نیست."})

        # محاسبه مجموع هزینه‌ها
        total_costs = sum(item.total_amount for item in report_data)

        # ارسال داده‌ها به کلاینت
        report = [{"category_name": item.category_name, "total_amount": item.total_amount} for item in report_data]

        return jsonify({
            "success": True,
            "report": report,
            "total_costs": total_costs  # ارسال مجموع هزینه‌ها به کلاینت
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
