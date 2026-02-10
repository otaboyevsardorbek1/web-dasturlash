import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'otaboyev-sardorbek-32905002Os!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Foydalanuvchilar ro'yxati
users = {}
user_count = 0

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global user_count
    user_count += 1
    
    # Yangi foydalanuvchi nomini yaratish
    user_id = f"user_{user_count}"
    users[user_id] = {'id': user_id, 'connected': True}
    
    # Foydalanuvchiga o'zining ID'sini yuborish
    emit('user_id', {'user_id': user_id})
    
    # Barcha foydalanuvchilarga yangi ulan haqida xabar
    current_time = datetime.now().strftime("%H:%M")
    message_data = {
        'type': 'system',
        'user': 'System',
        'message': f'✅ {user_id} chatga qo\'shildi',
        'time': current_time,
        'user_count': user_count
    }
    emit('message', message_data, broadcast=True)
    
    print(f"{user_id} ulandi. Jami foydalanuvchilar: {user_count}")

@socketio.on('disconnect')
def handle_disconnect():
    global user_count
    
    for user_id, user_data in users.items():
        if user_data.get('connected'):
            user_count -= 1
            users[user_id]['connected'] = False
            
            # Chiqib ketish xabarini yuborish
            current_time = datetime.now().strftime("%H:%M")
            message_data = {
                'type': 'system',
                'user': 'System',
                'message': f'🚪 {user_id} chatni tark etdi',
                'time': current_time,
                'user_count': user_count
            }
            emit('message', message_data, broadcast=True)
            
            print(f"{user_id} chiqdi. Jami foydalanuvchilar: {user_count}")
            break

@socketio.on('message')
def handle_message(data):
    current_time = datetime.now().strftime("%H:%M")
    
    message_data = {
        'type': 'user',
        'user': data.get('user', 'Anonim'),
        'message': data['message'],
        'time': current_time,
        'user_count': user_count
    }
    
    # Xabarni barcha foydalanuvchilarga yuborish
    emit('message', message_data, broadcast=True)
    
    # Konsolda ko'rsatish
    print(f"[{current_time}] {message_data['user']}: {message_data['message']}")

@socketio.on('typing')
def handle_typing(data):
    # Faqat boshqa foydalanuvchilarga typing xabarini yuborish
    emit('typing', {
        'user': data['user'],
        'is_typing': data['is_typing']
    }, broadcast=True, include_self=False)

if __name__ == '__main__':
    print("""
    ========================================
    WebSocket Chat Server ishga tushmoqda...
    ========================================
    Port: 5000
    URL: http://localhost:5000
    ========================================
    """)
    socketio.run(app, host='0.0.0.0', port=5000)