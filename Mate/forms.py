from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, SubmitField, PasswordField
from persiantools.jdatetime import JalaliDate

class LoginForm(FlaskForm):
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    submit = SubmitField('ورود')

class RegistrationForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    password = PasswordField('رمز عبور', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تکرار رمز عبور', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('ثبت‌نام')

class ExpenseForm(FlaskForm):
    amount = FloatField('مبلغ', validators=[DataRequired()])
    category = SelectField('دسته‌بندی', coerce=int, validators=[DataRequired()])
    description = TextAreaField('توضیحات')
    date = StringField('تاریخ', validators=[DataRequired()], default=JalaliDate.today().strftime('%Y-%m-%d'))
    submit = SubmitField('ثبت هزینه')
