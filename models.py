from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='default.png')
    bio = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - aniq nomlar bilan
    owned_groups = db.relationship('Group', back_populates='owner', lazy=True)
    group_memberships = db.relationship('GroupMember', back_populates='user', lazy=True)
    messages = db.relationship('Message', back_populates='user', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        return secrets.token_urlsafe(32)
    
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

# Group model
class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), default='group_default.png')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)
    invite_code = db.Column(db.String(50), unique=True, default=lambda: secrets.token_urlsafe(16))
    
    # Relationships - aniq nomlar bilan
    owner = db.relationship('User', back_populates='owned_groups', foreign_keys=[owner_id])
    members = db.relationship('GroupMember', back_populates='group', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', back_populates='group', lazy=True, cascade='all, delete-orphan')
    
    def is_owner(self, user):
        return self.owner_id == user.id
    
    def is_member(self, user):
        return GroupMember.query.filter_by(group_id=self.id, user_id=user.id).first() is not None
    
    def get_member_count(self):
        return len(self.members)
    
    def regenerate_invite_code(self):
        self.invite_code = secrets.token_urlsafe(16)
        db.session.commit()
    
    def __repr__(self):
        return f'<Group {self.name}>'

# Group Members model (many-to-many)
class GroupMember(db.Model):
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # owner, admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - MUHIM: back_populates bilan to'g'ri bog'lash
    group = db.relationship('Group', back_populates='members')
    user = db.relationship('User', back_populates='group_memberships')
    
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='unique_group_member'),)
    
    def is_admin(self):
        return self.role in ['owner', 'admin']
    
    def can_manage_messages(self):
        return self.role in ['owner', 'admin']
    
    def can_manage_members(self):
        return self.role in ['owner', 'admin']

# Message model with auto-delete
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(seconds=600))
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', back_populates='messages')
    group = db.relationship('Group', back_populates='messages')
    
    @classmethod
    def cleanup_expired(cls):
        expired = cls.query.filter(
            cls.expires_at <= datetime.utcnow(),
            cls.is_deleted == False
        ).all()
        
        for message in expired:
            message.is_deleted = True
            db.session.delete(message)
        
        db.session.commit()
        return len(expired)

# Password Reset Token model
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    is_used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User')
    
    @classmethod
    def cleanup_expired(cls):
        expired = cls.query.filter(cls.expires_at <= datetime.utcnow()).delete()
        db.session.commit()
        return expired

# User Activity Log
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User')