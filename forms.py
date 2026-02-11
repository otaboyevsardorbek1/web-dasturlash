from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username 3-80 belgi orasida bo\'lishi kerak')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Noto\'g\'ri email format'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Parol kamida 6 belgi bo\'lishi kerak')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Parollar mos kelmadi')
    ])
    submit = SubmitField('Ro\'yxatdan o\'tish')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu username allaqachon mavjud')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu email allaqachon ro\'yxatdan o\'tgan')

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Kirish')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Noto\'g\'ri email format')
    ])
    submit = SubmitField('Parolni tiklash')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Yangi parol', validators=[
        DataRequired(),
        Length(min=6, message='Parol kamida 6 belgi bo\'lishi kerak')
    ])
    confirm_password = PasswordField('Parolni tasdiqlang', validators=[
        DataRequired(),
        EqualTo('password', message='Parollar mos kelmadi')
    ])
    submit = SubmitField('Parolni yangilash')

class GroupForm(FlaskForm):
    name = StringField('Guruh nomi', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Guruh nomi 3-100 belgi orasida bo\'lishi kerak')
    ])
    description = TextAreaField('Tavsif', validators=[Length(max=500)])
    is_private = BooleanField('Shaxsiy guruh')
    submit = SubmitField('Yaratish')

class EditGroupForm(FlaskForm):
    name = StringField('Guruh nomi', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    description = TextAreaField('Tavsif', validators=[Length(max=500)])
    submit = SubmitField('Yangilash')

class InviteUserForm(FlaskForm):
    username = StringField('Foydalanuvchi nomi', validators=[DataRequired()])
    submit = SubmitField('Taklif qilish')