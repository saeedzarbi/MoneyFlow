from flask import  redirect, url_for, flash, Blueprint
from extensions import bcrypt, db
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm
from flask import render_template, request, jsonify
from models import db, Expense, Category, User, IncomeCategory, Income
import jdatetime
from datetime import datetime, timedelta
import pytz
from persiantools.jdatetime import JalaliDate
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def convert_persian_to_gregorian(date_str):
    try:
        # Split the date string into year, month, and day
        year, month, day = map(int, date_str.split('-'))
        
        # Convert Persian date to Gregorian using JalaliDate
        persian_date = JalaliDate(year, month, day)
        gregorian_date = persian_date.to_gregorian()
        
        return gregorian_date
    except (ValueError, TypeError) as e:
        print(f"Error converting date: {e}")
        return None

SLACK_WEBHOOK_URL = os.getenv('SLACK-HOOK')

def send_slack_notification(message):
    try:
        payload = {
            "text": message
        }
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Slack notification: {str(e)}")
        return False

auth_bp = Blueprint('auth', __name__)  

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True) 
            return redirect(url_for('auth.dashboard'))
        else:
            flash('login failed, please check your email and password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('email already exists', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('username already exists', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        # user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        
        flash('registration successful, please login', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  
# صفحه داشبورد
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    income_categories = IncomeCategory.query.all()

    return render_template('dashboard.html', categories=categories, income_categories=income_categories)

@auth_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    try:
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

        return jsonify({
            'message': 'دسته‌بندی جدید با موفقیت اضافه شد',
            'category_id': new_category.id,
            'category_name': new_category.name
        }), 201

    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint' in str(e):
            return jsonify({'error': 'این دسته‌بندی قبلاً ثبت شده است'}), 400
        return jsonify({'error': 'خطا در ثبت دسته‌بندی'}), 500

@auth_bp.route('/add_expense', methods=['POST'])
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
                return jsonify({"message": "all fields must be filled!"}), 400

            date_obj = convert_persian_to_gregorian(date_str)
            if not date_obj:
                return jsonify({"message": "invalid date format. use YYYY-MM-DD (persian)"}), 400

            category = Category.query.get(category_id)
            if not category:
                return jsonify({"message": "category not found"}), 404

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

            # Calculate monthly and daily expenses
            today_shamsi = jdatetime.date.today()
            current_year = today_shamsi.year
            current_month = today_shamsi.month

            # Monthly start and end dates
            month_start = jdatetime.date(current_year, current_month, 1).togregorian()
            if current_month == 12:
                month_end = jdatetime.date(current_year + 1, 1, 1).togregorian()
            else:
                month_end = jdatetime.date(current_year, current_month + 1, 1).togregorian()

            # Today's start and end dates
            today_start = jdatetime.date(current_year, current_month, today_shamsi.day).togregorian()
            today_end = jdatetime.date(current_year, current_month, today_shamsi.day + 1).togregorian()

            # Calculate monthly total
            monthly_expenses = Expense.query.filter(
                Expense.user_id == current_user.id,
                Expense.date >= month_start,
                Expense.date < month_end
            ).all()
            monthly_total = sum(exp.amount for exp in monthly_expenses)

            # Calculate today's total
            today_expenses = Expense.query.filter(
                Expense.user_id == current_user.id,
                Expense.date >= today_start,
                Expense.date < today_end
            ).all()
            today_total = sum(exp.amount for exp in today_expenses)

            # Send Slack notification
            persian_date = jdatetime.datetime.fromgregorian(datetime=date_obj).strftime('%Y/%m/%d')
            formatted_amount = "{:,.0f}".format(float(amount))
            formatted_monthly = "{:,.0f}".format(float(monthly_total))
            formatted_daily = "{:,.0f}".format(float(today_total))
            
            slack_message = f"🆕 هزینه جدید ثبت شد:\n👤 کاربر: {current_user.username}\n💰 مبلغ: {formatted_amount} تومان\n📁 دسته‌بندی: {category.name}\n📝 توضیحات: {description or 'ندارد'}\n📅 تاریخ: {persian_date}\n\n📊 خلاصه هزینه‌ها:\n📅 امروز: {formatted_daily} تومان\n📅 این ماه: {formatted_monthly} تومان"
            send_slack_notification(slack_message)

            return jsonify({
                "message": "expense added successfully!",
                "expense": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": expense.category.name,
                    "description": expense.description,
                    "date": expense.date.strftime('%Y-%m-%d')
                }
            })

        except Exception as e:
            return jsonify({"message": str(e)}), 500


@auth_bp.route('/report')
@login_required
def reports():
    return render_template('report.html')

@auth_bp.route('/get_all_report', methods=['GET'])
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
            return jsonify({"success": False, "message": "no report for this month."})

        total_costs = sum(item.total_amount for item in report_data)

        report = [{"category_id": item.category_id,"category_name": item.category_name, "total_amount": item.total_amount} for item in report_data]

        return jsonify({
            "success": True,
            "report": report,
            "total_costs": total_costs
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('/add_income_category', methods=['POST'])
@login_required
def add_income_category():
    try:
        data = request.get_json()
        category_name = data.get('incomeCategoryName')

        if not category_name:
            return jsonify({'error': 'نام دسته‌بندی نمی‌تواند خالی باشد'}), 400

        existing_category = IncomeCategory.query.filter_by(name=category_name).first()
        if existing_category:
            return jsonify({'error': 'این دسته‌بندی قبلاً ثبت شده است'}), 400

        new_category = IncomeCategory(name=category_name)
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            'message': 'دسته‌بندی درآمد جدید با موفقیت اضافه شد',
            'category_id': new_category.id,
            'category_name': new_category.name
        }), 201

    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint' in str(e):
            return jsonify({'error': 'این دسته‌بندی قبلاً ثبت شده است'}), 400
        return jsonify({'error': 'خطا در ثبت دسته‌بندی'}), 500

@auth_bp.route('/add_income', methods=['POST'])
@login_required
def add_income():
    if request.method == 'POST':
        try:
            data = request.get_json()
            amount = data.get('incomeAmount')
            category_id = data.get('incomeCategory')
            description = data.get('incomeDescription')
            date_str = data.get('date')

            if not amount or not category_id or not date_str:
                return jsonify({"message": "all fields must be filled!"}), 400

            date_obj = convert_persian_to_gregorian(date_str)
            if not date_obj:
                return jsonify({"message": "invalid date format. use YYYY-MM-DD (persian)"}), 400

            category = IncomeCategory.query.get(category_id)
            if not category:
                return jsonify({"message": "category not found"}), 404

            income = Income(
                amount=amount,
                category_id=category_id,
                user_id=current_user.id, 
                description=description
            )
            income.date = date_obj
            db.session.add(income)
            db.session.commit()

            # Send Slack notification
            persian_date = jdatetime.datetime.fromgregorian(datetime=income.date).strftime('%Y/%m/%d')
            formatted_amount = "{:,.0f}".format(float(amount))
            slack_message = f"🆕 درآمد جدید ثبت شد:\n👤 کاربر: {current_user.username}\n💰 مبلغ: {formatted_amount} تومان\n📁 دسته‌بندی: {category.name}\n📝 توضیحات: {description or 'ندارد'}\n📅 تاریخ: {persian_date}"
            send_slack_notification(slack_message)

            return jsonify({
                "message": "income added successfully!",
                "income": {
                    "id": income.id,
                    "amount": income.amount,
                    "category": income.category.name,
                    "description": income.description,
                    "date": income.date.strftime('%Y/%m/%d')
                }
            })

        except Exception as e:
            return jsonify({"message": "error in adding income. please try again."}), 500

@auth_bp.route('/get_income_report', methods=['GET'])
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
            IncomeCategory.id.label('category_id'),
            db.func.sum(Income.amount).label('total_amount')
        ).join(Income).filter(
            Income.user_id == current_user.id,
            Income.date >= start_date,
            Income.date < end_date
        ).group_by(IncomeCategory.id).all()

        if not report_data:
            return jsonify({"success": False, "message": "no report for this month."})

        # محاسبه مجموع درآمدها
        total_income = sum(item.total_amount for item in report_data)

        # ارسال داده‌ها به کلاینت
        income_report = [{
            "category_id": item.category_id,
            "category_name": item.category_name, 
            "total_amount": item.total_amount
        } for item in report_data]

        return jsonify({
            "success": True,
            "income_report": income_report,
            "total_income": total_income
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('/expenses/<int:category_id>', methods=['GET'])
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
            return jsonify({"success": False, "message": "no expense for this category in this month."})

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

@auth_bp.route('/detail/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    try:
        expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()

        if not expense:
            return jsonify({"success": False, "message": "expense not found or you don't have access to it."}), 404

        # حذف هزینه از دیتابیس
        db.session.delete(expense)
        db.session.commit()

        return jsonify({"success": True, "message": "expense deleted successfully."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"error in deleting expense: {str(e)}"}), 500

@auth_bp.route('/incomes/<int:category_id>', methods=['GET'])
@login_required
def get_category_incomes(category_id):
    try:
        today_shamsi = jdatetime.date.today()
        current_year = today_shamsi.year
        current_month = today_shamsi.month

        start_date = jdatetime.date(current_year, current_month, 1).togregorian()
        if current_month == 12:
            end_date = jdatetime.date(current_year + 1, 1, 1).togregorian()
        else:
            end_date = jdatetime.date(current_year, current_month + 1, 1).togregorian()

        incomes = Income.query.filter(
            Income.user_id == current_user.id,
            Income.category_id == category_id,
            Income.date >= start_date,
            Income.date < end_date
        ).all()

        if not incomes:
            return jsonify({"success": False, "message": "no income for this category in this month."})

        income_list = [{
            "id": inc.id,
            "amount": inc.amount,
            "description": inc.description,
            "date": jdatetime.datetime.fromgregorian(datetime=inc.date).strftime('%Y/%m/%d')
        } for inc in incomes]

        return jsonify({
            "success": True,
            "incomes": income_list
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('/income-detail/<int:income_id>', methods=['DELETE'])
@login_required
def delete_income(income_id):
    try:
        income = Income.query.filter_by(id=income_id, user_id=current_user.id).first()

        if not income:
            return jsonify({"success": False, "message": "income not found or you don't have access to it."}), 404

        db.session.delete(income)
        db.session.commit()

        return jsonify({"success": True, "message": "income deleted successfully."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"error in deleting income: {str(e)}"}), 500

@auth_bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@auth_bp.route('/get_monthly_analysis', methods=['GET'])
@login_required
def get_monthly_analysis():
    try:
        # Get query parameters
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        # If no year/month provided, use current
        if not year or not month:
            today_shamsi = jdatetime.date.today()
            year = today_shamsi.year
            month = today_shamsi.month

        # Convert to Gregorian dates for database query
        start_date = jdatetime.date(year, month, 1).togregorian()
        if month == 12:
            end_date = jdatetime.date(year + 1, 1, 1).togregorian()
        else:
            end_date = jdatetime.date(year, month + 1, 1).togregorian()

        # Get expenses by category with Jalali date filtering
        expenses = db.session.query(
            Category.name.label('category'),
            db.func.sum(Expense.amount).label('amount')
        ).join(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.date >= start_date,
            Expense.date < end_date
        ).group_by(Category.name).all()

        # Get incomes by category with Jalali date filtering
        incomes = db.session.query(
            IncomeCategory.name.label('category'),
            db.func.sum(Income.amount).label('amount')
        ).join(Income).filter(
            Income.user_id == current_user.id,
            Income.date >= start_date,
            Income.date < end_date
        ).group_by(IncomeCategory.name).all()

        # Get daily expenses for the month
        daily_expenses = []
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + timedelta(days=1)
            daily_amount = db.session.query(
                db.func.sum(Expense.amount)
            ).filter(
                Expense.user_id == current_user.id,
                Expense.date >= current_date,
                Expense.date < next_date
            ).scalar() or 0

            if daily_amount > 0:
                daily_expenses.append({
                    "date": jdatetime.date.fromgregorian(date=current_date).strftime('%Y/%m/%d'),
                    "amount": daily_amount
                })
            
            current_date = next_date

        # Calculate totals
        total_expense = sum(exp.amount for exp in expenses)
        total_income = sum(inc.amount for inc in incomes)
        net_savings = total_income - total_expense

        # Format the response
        analysis = {
            "year": year,
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_savings": net_savings,
            "savings_percentage": (net_savings / total_income * 100) if total_income > 0 else 0,
            "expense_breakdown": [
                {"category": exp.category, "amount": exp.amount, 
                 "percentage": (exp.amount / total_expense * 100) if total_expense > 0 else 0}
                for exp in expenses
            ],
            "income_breakdown": [
                {"category": inc.category, "amount": inc.amount,
                 "percentage": (inc.amount / total_income * 100) if total_income > 0 else 0}
                for inc in incomes
            ],
            "daily_expenses": daily_expenses
        }

        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('/get_yearly_summary', methods=['GET'])
@login_required
def get_yearly_summary():
    try:
        year = request.args.get('year', type=int)
        if not year:
            year = jdatetime.date.today().year

        yearly_data = []
        
        for month in range(1, 13):
            # Convert Persian date to Gregorian for each month
            start_date = jdatetime.date(year, month, 1).togregorian()
            if month == 12:
                end_date = jdatetime.date(year + 1, 1, 1).togregorian()
            else:
                end_date = jdatetime.date(year, month + 1, 1).togregorian()

            # Get monthly totals with Gregorian date conversion
            monthly_expense = db.session.query(
                db.func.sum(Expense.amount)
            ).filter(
                Expense.user_id == current_user.id,
                Expense.date >= start_date,
                Expense.date < end_date
            ).scalar() or 0

            monthly_income = db.session.query(
                db.func.sum(Income.amount)
            ).filter(
                Income.user_id == current_user.id,
                Income.date >= start_date,
                Income.date < end_date
            ).scalar() or 0

            yearly_data.append({
                "month": month,
                "month_name": ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
                              "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"][month - 1],
                "total_expense": monthly_expense,
                "total_income": monthly_income,
                "net_savings": monthly_income - monthly_expense
            })

        # Calculate yearly totals
        total_yearly_income = sum(month["total_income"] for month in yearly_data)
        total_yearly_expense = sum(month["total_expense"] for month in yearly_data)
        
        return jsonify({
            "success": True,
            "year": year,
            "yearly_summary": yearly_data,
            "yearly_totals": {
                "total_income": total_yearly_income,
                "total_expense": total_yearly_expense,
                "net_savings": total_yearly_income - total_yearly_expense
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@auth_bp.route('/get_categories', methods=['GET'])
@login_required
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify({
            "success": True,
            "categories": [{"id": cat.id, "name": cat.name} for cat in categories]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/get_income_categories', methods=['GET'])
@login_required
def get_income_categories():
    try:
        categories = IncomeCategory.query.all()
        return jsonify({
            "success": True,
            "categories": [{"id": cat.id, "name": cat.name} for cat in categories]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/get_recent_expenses', methods=['GET'])
@login_required
def get_recent_expenses():
    try:
        # Get the last 10 expenses
        expenses = Expense.query.filter_by(user_id=current_user.id)\
            .order_by(Expense.date.desc())\
            .limit(10)\
            .all()

        expense_list = []
        for expense in expenses:
            persian_date = jdatetime.datetime.fromgregorian(datetime=expense.date).strftime('%Y/%m/%d')
            expense_list.append({
                "id": expense.id,
                "amount": expense.amount,
                "category": expense.category.name,
                "description": expense.description,
                "date": persian_date
            })

        return jsonify(expense_list)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/get_recent_incomes', methods=['GET'])
@login_required
def get_recent_incomes():
    try:
        # Get the last 10 incomes
        incomes = Income.query.filter_by(user_id=current_user.id)\
            .order_by(Income.date.desc())\
            .limit(10)\
            .all()

        income_list = []
        for income in incomes:
            persian_date = jdatetime.datetime.fromgregorian(datetime=income.date).strftime('%Y/%m/%d')
            income_list.append({
                "id": income.id,
                "amount": income.amount,
                "category": income.category.name,
                "description": income.description,
                "date": persian_date
            })

        return jsonify(income_list)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/delete_expense_category', methods=['POST'])
@login_required
def delete_expense_category():
    try:
        data = request.get_json()
        category_id = data.get('category_id')

        if not category_id:
            return jsonify({'success': False, 'message': 'شناسه دسته‌بندی الزامی است'}), 400

        # بررسی وجود دسته‌بندی
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'message': 'دسته‌بندی یافت نشد'}), 404

        # بررسی وجود هزینه‌های مرتبط
        expenses = Expense.query.filter_by(category_id=category_id).first()
        if expenses:
            return jsonify({'success': False, 'message': 'این دسته‌بندی دارای هزینه است و نمی‌توان آن را حذف کرد'}), 400

        # حذف دسته‌بندی
        db.session.delete(category)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'دسته‌بندی با موفقیت حذف شد'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'خطا در حذف دسته‌بندی: {str(e)}'}), 500

@auth_bp.route('/delete_income_category', methods=['POST'])
@login_required
def delete_income_category():
    try:
        data = request.get_json()
        category_id = data.get('category_id')

        if not category_id:
            return jsonify({'success': False, 'message': 'شناسه دسته‌بندی الزامی است'}), 400

        # بررسی وجود دسته‌بندی
        category = IncomeCategory.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'message': 'دسته‌بندی یافت نشد'}), 404

        # بررسی وجود درآمدهای مرتبط
        incomes = Income.query.filter_by(category_id=category_id).first()
        if incomes:
            return jsonify({'success': False, 'message': 'این دسته‌بندی دارای درآمد است و نمی‌توان آن را حذف کرد'}), 400

        # حذف دسته‌بندی
        db.session.delete(category)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'دسته‌بندی با موفقیت حذف شد'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'خطا در حذف دسته‌بندی: {str(e)}'}), 500

