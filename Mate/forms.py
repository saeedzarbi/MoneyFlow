from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, SubmitField, PasswordField
from persiantools.jdatetime import JalaliDate

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ExpenseForm(FlaskForm):
    amount = FloatField('مبلغ', validators=[DataRequired()])
    category = SelectField('دسته‌بندی', coerce=int, validators=[DataRequired()])
    description = TextAreaField('توضیحات')
    date = StringField('تاریخ', validators=[DataRequired()], default=JalaliDate.today().strftime('%Y-%m-%d'))
    submit = SubmitField('ثبت هزینه')
