from flask_login import UserMixin
from persiantools.jdatetime import JalaliDateTime
from datetime import datetime
import pytz
from extensions import db, bcrypt

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tehran')))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category = db.relationship('Category', backref=db.backref('expenses', lazy=True))
    user = db.relationship('User', backref=db.backref('expenses', lazy=True))

    def __init__(self, amount, category_id, user_id, description=None):
        self.amount = amount
        self.category_id = category_id
        self.user_id = user_id
        self.description = description
        self.date = datetime.now(pytz.timezone('Asia/Tehran'))

    def get_persian_date(self):
        return JalaliDateTime(self.date).strftime('%Y/%m/%d')

class IncomeCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tehran')))
    category_id = db.Column(db.Integer, db.ForeignKey('income_category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category = db.relationship('IncomeCategory', backref=db.backref('incomes', lazy=True))
    user = db.relationship('User', backref=db.backref('incomes', lazy=True))

    def __init__(self, amount, category_id, user_id, description=None):
        self.amount = amount
        self.category_id = category_id
        self.user_id = user_id
        self.description = description
        self.date = datetime.now(pytz.timezone('Asia/Tehran'))

    def get_persian_date(self):
        return JalaliDateTime(self.date).strftime('%Y/%m/%d')
