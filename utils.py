import os
import secrets
import datetime
from PIL import Image
from flask import current_app, url_for
from flask_mail import Message
from threading import Thread

def save_image(image, folder='avatars'):
    """Rasmni saqlash va optimize qilish"""
    # Generate random filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image.filename)
    filename = f"{random_hex}{f_ext}"
    
    # Create folder if not exists
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Save and optimize image
    filepath = os.path.join(upload_path, filename)
    
    # Resize image if too large
    img = Image.open(image)
    
    # Max dimensions
    if folder == 'avatars':
        max_size = (200, 200)
    elif folder.startswith('group'):
        max_size = (400, 400)
    else:
        max_size = (800, 800)
    
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save with optimization
    if img.mode in ('RGBA', 'LA'):
        # Convert to RGB for JPEG
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        rgb_img.save(filepath, optimize=True, quality=85)
    else:
        img.save(filepath, optimize=True, quality=85)
    
    return f'uploads/{folder}/{filename}'

def delete_image(filepath, folder='avatars'):
    """Rasmni o'chirish"""
    if not filepath or 'default' in filepath:
        return
    
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                            folder, 
                            os.path.basename(filepath))
    
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False

def send_async_email(app, msg):
    """Email yuborish (async)"""
    with app.app_context():
        from flask_mail import Mail
        mail = Mail(app)
        mail.send(msg)

def send_password_reset_email(user, token):
    """Parolni tiklash emaili yuborish"""
    from flask_mail import Message
    
    msg = Message()
    msg.subject = 'WebSocket Chat - Parolni tiklash'
    msg.sender = current_app.config['MAIL_DEFAULT_SENDER']
    msg.recipients = [user.email]
    
    reset_url = url_for('auth.reset_token', token=token, _external=True)
    
    msg.html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(to right, #4f46e5, #7c3aed);
                border-radius: 10px;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 8px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(to right, #4f46e5, #7c3aed);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h2>Parolni tiklash</h2>
                <p>Assalomu alaykum, {user.username}!</p>
                <p>Parolingizni tiklash uchun quyidagi tugmani bosing:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Parolni tiklash</a>
                </p>
                <p>Agar siz parolni tiklash so'rovini yubormagan bo'lsangiz, ushbu xabarni e'tiborsiz qoldiring.</p>
                <p>Bu havola <strong>1 soat</strong> davomida amal qiladi.</p>
                <hr>
                <small>WebSocket Chat - Real vaqtli chat platformasi</small>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        Thread(target=send_async_email, 
               args=(current_app._get_current_object(), msg)).start()
        return True
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")
        return False

def cleanup_expired_messages():
    """Muddati o'tgan xabarlarni o'chirish (cron job)"""
    from models import Message
    return Message.cleanup_expired()

def format_timestamp(timestamp):
    """Vaqtni formatlash"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days == 0:
        if diff.seconds < 60:
            return 'hozir'
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f'{minutes} daqiqa oldin'
        else:
            return timestamp.strftime('%H:%M')
    elif diff.days == 1:
        return 'kecha'
    elif diff.days < 7:
        return f'{diff.days} kun oldin'
    else:
        return timestamp.strftime('%d.%m.%Y')