from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import secrets

from models import db, User, PasswordResetToken, ActivityLog
from forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from utils import send_password_reset_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        log = ActivityLog(
            user_id=user.id,
            action='register',
            details=f'User registered with email: {user.email}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Muvaffaqiyatli ro\'yxatdan o\'tdingiz! Endi tizimga kirishingiz mumkin.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Username or email bilan qidirish
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.is_online = True
            user.update_last_seen()
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                action='login',
                details='User logged in',
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            flash(f'Xush kelibsiz, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Noto\'g\'ri username/email yoki parol', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    user = current_user
    user.is_online = False
    user.update_last_seen()
    
    # Log activity
    log = ActivityLog(
        user_id=user.id,
        action='logout',
        details='User logged out',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('Tizimdan chiqdingiz', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate token
            token = secrets.token_urlsafe(32)
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token
            )
            db.session.add(reset_token)
            db.session.commit()
            
            # Send email
            if send_password_reset_email(user, token):
                flash('Parolni tiklash bo\'yicha ko\'rsatmalar email manzilingizga yuborildi', 'info')
            else:
                flash('Email yuborishda xatolik yuz berdi. Iltimos qayta urinib ko\'ring.', 'danger')
        else:
            # Xavfsizlik uchun - user mavjud bo'lmasa ham xabar bir xil
            flash('Parolni tiklash bo\'yicha ko\'rsatmalar email manzilingizga yuborildi', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_request.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Find valid token
    reset_token = PasswordResetToken.query.filter_by(
        token=token,
        is_used=False
    ).first()
    
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        flash('Noto\'g\'ri yoki muddati o\'tgan token', 'danger')
        return redirect(url_for('auth.reset_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.get(reset_token.user_id)
        user.password = form.password.data
        
        # Mark token as used
        reset_token.is_used = True
        
        db.session.commit()
        
        flash('Parolingiz muvaffaqiyatli yangilandi! Endi tizimga kirishingiz mumkin.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_token.html', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Update user profile
        current_user.bio = request.form.get('bio', '')
        
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                from utils import save_image
                filename = save_image(file, 'avatars')
                if filename:
                    current_user.avatar = filename
        
        db.session.commit()
        flash('Profil muvaffaqiyatli yangilandi', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=current_user)