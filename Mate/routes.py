from flask import  redirect, url_for, flash, Blueprint
from extensions import bcrypt, db
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm
from flask import render_template, request, jsonify
from models import db, Expense, Category, User, IncomeCategory, Income
import jdatetime
from datetime import datetime
import pytz
from persiantools.jdatetime import JalaliDate

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)  # فعال کردن کوکی Remember-Me
            return redirect(url_for('auth.dashboard'))
        else:
            flash('ورود ناموفق. لطفاً ایمیل و پسورد را بررسی کنید.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # هدایت به صفحه لاگین

# صفحه داشبورد
@auth_bp.route('dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    income_categories = IncomeCategory.query.all()

    return render_template('dashboard.html', categories=categories, income_categories=income_categories)

@auth_bp.route('add_category', methods=['POST'])
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


def convert_persian_to_gregorian(date_str):

    try:
        date_str = date_str.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        year, month, day = map(int, date_str.split('-'))
        gregorian_date = JalaliDate(year, month, day).to_gregorian()

        return datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day,
                        tzinfo=pytz.timezone('Asia/Tehran'))
    except ValueError:
        return None

@auth_bp.route('add_expense', methods=['POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            data = request.get_json()
            amount = data.get('amount')
            category_id = data.get('category')
            description = data.get('description')
            date_str = data.get('date')

            if not amount or not category_id or not date_str:
                return jsonify({"message": "تمامی فیلدها باید پر شوند!"}), 400

            date_obj = convert_persian_to_gregorian(date_str)
            print(date_obj)
            if not date_obj:
                return jsonify({"message": "فرمت تاریخ نامعتبر است. از YYYY-MM-DD (شمسی) استفاده کنید."}), 400

            # ایجاد و ذخیره هزینه
            expense = Expense(
                amount=amount,
                category_id=category_id,
                user_id=current_user.id,
                description=description,
                date=date_obj
            )
            db.session.add(expense)
            db.session.commit()

            return jsonify({
                "message": "هزینه با موفقیت ثبت شد!",
                "expense": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": expense.category.name,
                    "description": expense.description,
                    "date": expense.date.strftime('%Y-%m-%d')
                }
            })

        except Exception as e:
            return jsonify({"message": "خطا در ثبت هزینه. لطفاً دوباره تلاش کنید."}), 500


@auth_bp.route('report')
@login_required
def reports():
    return render_template('report.html')

@auth_bp.route('get_all_report', methods=['GET'])
@login_required
def get_monthly_report():
    try:
        # دریافت تاریخ امروز به شمسی
        today_shamsi = jdatetime.date.today()
        current_year = today_shamsi.year
        current_month = today_shamsi.month

        # تبدیل تاریخ شمسی به میلادی برای فیلتر کردن رکوردهای دیتابیس
        start_date = jdatetime.date(current_year, current_month, 1).togregorian()
        if current_month == 12:
            end_date = jdatetime.date(current_year + 1, 1, 1).togregorian()
        else:
            end_date = jdatetime.date(current_year, current_month + 1, 1).togregorian()

        report_data = db.session.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            db.func.sum(Expense.amount).label('total_amount')
        ).join(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.date >= start_date,
            Expense.date < end_date
        ).group_by(Category.id).all()

        if not report_data:
            return jsonify({"success": False, "message": "هیچ گزارشی برای این ماه شمسی موجود نیست."})

        # محاسبه مجموع هزینه‌ها
        total_costs = sum(item.total_amount for item in report_data)

        # ارسال داده‌ها به کلاینت
        report = [{"category_id": item.category_id,"category_name": item.category_name, "total_amount": item.total_amount} for item in report_data]

        return jsonify({
            "success": True,
            "report": report,
            "total_costs": total_costs
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('add_income_category', methods=['POST'])
@login_required
def add_income_category():
    data = request.get_json()
    category_name = data.get('incomeCategoryName')

    if not category_name:
        return jsonify({'error': 'نام دسته‌بندی نمی‌تواند خالی باشد'}), 400

    existing_category = IncomeCategory.query.filter_by(name=category_name).first()
    if existing_category:
        return jsonify({'error': 'این دسته‌بندی درآمد قبلاً ثبت شده است'}), 400

    new_category = IncomeCategory(name=category_name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        'message': 'دسته‌بندی درآمد جدید با موفقیت ثبت شد',
        'category_id': new_category.id,
        'category_name': new_category.name
    }), 201

@auth_bp.route('add_income', methods=['POST'])
@login_required
def add_income():
    if request.method == 'POST':
        try:
            data = request.get_json()
            amount = data.get('incomeAmount')
            category_id = data.get('incomeCategory')
            description = data.get('incomeDescription')

            # بررسی صحت داده‌ها
            if not amount or not category_id:
                return jsonify({"message": "تمامی فیلدها باید پر شوند!"}), 400

            # اضافه کردن درآمد جدید به پایگاه داده
            income = Income(
                amount=amount,
                category_id=category_id,
                user_id=current_user.id,  # کاربری که وارد شده است
                description=description
            )
            db.session.add(income)
            db.session.commit()

            # ارسال پاسخ به کاربر
            return jsonify({
                "message": "درآمد با موفقیت ثبت شد!",
                "income": {
                    "id": income.id,
                    "amount": income.amount,
                    "category": income.category.name,
                    "description": income.description,
                    "date": income.date.strftime('%Y/%m/%d')
                }
            })

        except Exception as e:
            return jsonify({"message": "خطا در ثبت درآمد. لطفاً دوباره تلاش کنید."}), 500

@auth_bp.route('get_income_report', methods=['GET'])
@login_required
def get_income_report():
    try:
        # دریافت تاریخ امروز به شمسی
        today_shamsi = jdatetime.date.today()
        current_year = today_shamsi.year
        current_month = today_shamsi.month

        # تبدیل تاریخ شمسی به میلادی برای استفاده در فیلتر دیتابیس
        start_date = jdatetime.date(current_year, current_month, 1).togregorian()
        if current_month == 12:
            end_date = jdatetime.date(current_year + 1, 1, 1).togregorian()
        else:
            end_date = jdatetime.date(current_year, current_month + 1, 1).togregorian()

        # دریافت درآمدها بر اساس دسته‌بندی و فیلتر بر اساس ماه شمسی
        report_data = db.session.query(
            IncomeCategory.name.label('category_name'),
            db.func.sum(Income.amount).label('total_amount')
        ).join(Income).filter(
            Income.user_id == current_user.id,
            Income.date >= start_date,
            Income.date < end_date
        ).group_by(IncomeCategory.id).all()

        if not report_data:
            return jsonify({"success": False, "message": "هیچ گزارشی برای درآمد این ماه موجود نیست."})

        # محاسبه مجموع درآمدها
        total_income = sum(item.total_amount for item in report_data)

        # ارسال داده‌ها به کلاینت
        income_report = [{"category_name": item.category_name, "total_amount": item.total_amount} for item in report_data]

        return jsonify({
            "success": True,
            "income_report": income_report,
            "total_income": total_income  # ارسال مجموع درآمدها به کلاینت
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('expenses/<int:category_id>', methods=['GET'])
@login_required
def get_category_expenses(category_id):
    try:
        today_shamsi = jdatetime.date.today()
        current_year = today_shamsi.year
        current_month = today_shamsi.month

        start_date = jdatetime.date(current_year, current_month, 1).togregorian()
        if current_month == 12:
            end_date = jdatetime.date(current_year + 1, 1, 1).togregorian()
        else:
            end_date = jdatetime.date(current_year, current_month + 1, 1).togregorian()

        expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.category_id == category_id,
            Expense.date >= start_date,
            Expense.date < end_date
        ).all()

        if not expenses:
            return jsonify({"success": False, "message": "هیچ هزینه‌ای برای این دسته‌بندی در این ماه یافت نشد."})

        expense_list = [{
            "id": exp.id,
            "amount": exp.amount,
            "description": exp.description,
            "date": jdatetime.datetime.fromgregorian(datetime=exp.date).strftime('%Y/%m/%d')
        } for exp in expenses]

        return jsonify({
            "success": True,
            "expenses": expense_list
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('detail/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    try:
        expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()

        if not expense:
            return jsonify({"success": False, "message": "هزینه موردنظر یافت نشد یا شما دسترسی به آن ندارید."}), 404

        # حذف هزینه از دیتابیس
        db.session.delete(expense)
        db.session.commit()

        return jsonify({"success": True, "message": "هزینه با موفقیت حذف شد."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"خطا در حذف هزینه: {str(e)}"}), 500

