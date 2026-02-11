from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os

from models import db, Message, Group, GroupMember
from utils import save_image, delete_image

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/groups/<int:group_id>/messages', methods=['POST'])
@login_required
def send_message(group_id):
    """Xabar yuborish"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is member
    if not group.is_member(current_user):
        return jsonify({'error': 'Siz bu guruh a\'zosi emassiz'}), 403
    
    content = request.form.get('content', '').strip()
    
    # Handle image upload
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = save_image(file, f'group_{group_id}_images')
            if filename:
                image_url = filename
    
    if not content and not image_url:
        return jsonify({'error': 'Xabar yoki rasm yuborishingiz kerak'}), 400
    
    # Create message (expires in 10 minutes)
    message = Message(
        user_id=current_user.id,
        group_id=group_id,
        content=content,
        image_url=image_url,
        expires_at=datetime.utcnow() + timedelta(seconds=600)
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Emit via Socket.IO
    from app import socketio
    socketio.emit('new_group_message', {
        'id': message.id,
        'user': current_user.username,
        'user_id': current_user.id,
        'content': content,
        'image_url': image_url,
        'created_at': message.created_at.isoformat(),
        'expires_at': message.expires_at.isoformat(),
        'group_id': group_id
    }, room=f'group_{group_id}')
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'content': content,
            'image_url': image_url,
            'created_at': message.created_at.isoformat()
        }
    })

@messages_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Xabarni o'chirish"""
    message = Message.query.get_or_404(message_id)
    
    # Check permissions
    member = GroupMember.query.filter_by(
        group_id=message.group_id,
        user_id=current_user.id
    ).first()
    
    # User can delete their own messages or if they have manage permissions
    if message.user_id != current_user.id and (not member or not member.can_manage_messages()):
        return jsonify({'error': 'Bu xabarni o\'chirishga ruxsat yo\'q'}), 403
    
    # Delete image if exists
    if message.image_url:
        delete_image(message.image_url, f'group_{message.group_id}_images')
    
    db.session.delete(message)
    db.session.commit()
    
    # Emit deletion event
    from app import socketio
    socketio.emit('delete_group_message', {
        'message_id': message_id,
        'group_id': message.group_id
    }, room=f'group_{message.group_id}')
    
    return jsonify({'success': True})

@messages_bp.route('/messages/<int:message_id>', methods=['GET'])
@login_required
def get_message(message_id):
    """Xabarni olish"""
    message = Message.query.get_or_404(message_id)
    
    # Check if user has access to the group
    if not message.group.is_member(current_user):
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    return jsonify({
        'id': message.id,
        'user': message.user.username,
        'user_id': message.user_id,
        'content': message.content,
        'image_url': message.image_url,
        'created_at': message.created_at.isoformat(),
        'expires_at': message.expires_at.isoformat(),
        'group_id': message.group_id
    })

@messages_bp.route('/groups/<int:group_id>/messages')
@login_required
def get_messages(group_id):
    """Guruh xabarlarini olish"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is member
    if not group.is_member(current_user):
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    # Cleanup expired messages first
    Message.cleanup_expired()
    
    limit = request.args.get('limit', 50, type=int)
    before = request.args.get('before')
    
    query = Message.query.filter_by(
        group_id=group_id,
        is_deleted=False
    )
    
    if before:
        query = query.filter(Message.id < int(before))
    
    messages = query.order_by(Message.created_at.desc()).limit(limit).all()
    
    return jsonify([{
        'id': msg.id,
        'user': msg.user.username,
        'user_avatar': msg.user.avatar,
        'content': msg.content,
        'image_url': msg.image_url,
        'created_at': msg.created_at.isoformat(),
        'expires_at': msg.expires_at.isoformat()
    } for msg in messages])