import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, current_user, login_required
from datetime import datetime, timedelta
import os
import json

# Import modules
from config import Config
from models import db, User, Group, GroupMember, Message, ActivityLog
from auth import auth_bp
from groups import groups_bp
from messages import messages_bp
from utils import cleanup_expired_messages

# Initialize app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Iltimos, tizimga kiring'
login_manager.login_message_category = 'info'

socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   async_mode='eventlet',
                   ping_timeout=60,
                   ping_interval=25)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(groups_bp, url_prefix='/groups')
app.register_blueprint(messages_bp, url_prefix='/api')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Main route
@app.route('/')
@login_required
def index():
    return render_template('chat.html')

# Uploads route
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)

# SocketIO events
@socketio.on('connect')
@login_required
def handle_connect():
    """Client ulanganda"""
    print(f"✅ {current_user.username} ulandi")
    
    # Update user status
    current_user.is_online = True
    current_user.update_last_seen()
    
    # Join user's groups
    user_groups = GroupMember.query.filter_by(user_id=current_user.id).all()
    for member in user_groups:
        room = f"group_{member.group_id}"
        join_room(room)
        print(f"📌 {current_user.username} joined room: {room}")
    
    # Emit online status
    emit('user_online', {'user_id': current_user.id, 'username': current_user.username}, broadcast=True)

@socketio.on('disconnect')
@login_required
def handle_disconnect():
    """Client uzilganda"""
    print(f"❌ {current_user.username} uzildi")
    
    # Update user status
    current_user.is_online = False
    current_user.update_last_seen()
    
    # Emit offline status
    emit('user_offline', {'user_id': current_user.id, 'username': current_user.username}, broadcast=True)

@socketio.on('join_group')
@login_required
def handle_join_group(data):
    """Guruh xonasiga qo'shilish"""
    group_id = data.get('group_id')
    group = Group.query.get_or_404(group_id)
    
    # Check if user is member
    if group.is_member(current_user):
        room = f"group_{group_id}"
        join_room(room)
        print(f"📌 {current_user.username} joined group room: {room}")
        
        emit('group_joined', {
            'group_id': group_id,
            'username': current_user.username
        }, room=room)

@socketio.on('leave_group')
@login_required
def handle_leave_group(data):
    """Guruh xonasidan chiqish"""
    group_id = data.get('group_id')
    room = f"group_{group_id}"
    leave_room(room)
    
    emit('group_left', {
        'group_id': group_id,
        'username': current_user.username
    }, room=room)

@socketio.on('typing_group')
@login_required
def handle_typing_group(data):
    """Guruhda yozayotganligi haqida xabar"""
    group_id = data.get('group_id')
    is_typing = data.get('is_typing', False)
    
    room = f"group_{group_id}"
    emit('user_typing', {
        'user_id': current_user.id,
        'username': current_user.username,
        'is_typing': is_typing
    }, room=room, include_self=False)

# Cleanup task (runs every minute)
@socketio.on('start_cleanup')
def handle_cleanup():
    """Muddati o'tgan xabarlarni o'chirish"""
    import threading
    import time
    
    def cleanup_job():
        while True:
            time.sleep(60)  # Every minute
            with app.app_context():
                deleted_count = cleanup_expired_messages()
                if deleted_count > 0:
                    print(f"🧹 {deleted_count} ta muddati o'tgan xabar o'chirildi")
                    socketio.emit('cleanup_complete', {
                        'deleted_count': deleted_count,
                        'timestamp': datetime.utcnow().isoformat()
                    })
    
    thread = threading.Thread(target=cleanup_job, daemon=True)
    thread.start()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create upload folders
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'group_avatars'), exist_ok=True)
    
    print("""
    ============================================
    🚀 WebSocket Chat Server ishga tushmoqda...
    ============================================
    Port: 5000
    URL: http://localhost:5000
    Database: SQLite
    Auto-delete: 10 minutes
    ============================================
    """)
    
    # Start cleanup job
    socketio.start_background_task(handle_cleanup)
    
    socketio.run(app, host='0.0.0.0', port=5000,debug=True)