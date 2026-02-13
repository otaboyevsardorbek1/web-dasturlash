from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from models import db, Group, GroupMember, Message, User
from forms import GroupForm, EditGroupForm, InviteUserForm
from utils import save_image, delete_image

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/groups')
@login_required
def list_groups():
    """Foydalanuvchi a'zo bo'lgan guruhlar"""
    user_groups = GroupMember.query.filter_by(user_id=current_user.id).all()
    groups = [member.group for member in user_groups]
    
    # Ochiq guruhlar (taklif qilish mumkin)
    public_groups = Group.query.filter_by(is_private=False).all()
    
    return render_template('groups/list.html', 
                         groups=groups, 
                         public_groups=public_groups)

@groups_bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """Yangi guruh yaratish"""
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            owner_id=current_user.id,
            is_private=form.is_private.data
        )
        
        # Handle group avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = save_image(file, 'group_avatars')
                if filename:
                    group.avatar = filename
        
        db.session.add(group)
        db.session.flush()
        
        # Add owner as member with owner role
        member = GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            role='owner'
        )
        db.session.add(member)
        db.session.commit()
        
        flash(f'Guruh "{group.name}" muvaffaqiyatli yaratildi!', 'success')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    return render_template('groups/create.html', form=form)

@groups_bp.route('/groups/<int:group_id>')
@login_required
def view_group(group_id):
    """Guruh sahifasini ko'rish"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is member
    member = GroupMember.query.filter_by(
        group_id=group_id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        # Check if group is public
        if not group.is_private:
            # Auto-join public groups
            new_member = GroupMember(
                group_id=group_id,
                user_id=current_user.id,
                role='member'
            )
            db.session.add(new_member)
            db.session.commit()
            member = new_member
        else:
            flash('Bu guruhga kirish uchun ruxsat yo\'q', 'danger')
            return redirect(url_for('groups.list_groups'))
    
    # Get recent messages
    messages = Message.query.filter_by(
        group_id=group_id, 
        is_deleted=False
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    # Get members
    members = GroupMember.query.filter_by(group_id=group_id).all()
    
    return render_template('groups/view.html', 
                         group=group, 
                         messages=messages, 
                         members=members,
                         member=member)

@groups_bp.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    """Guruh ma'lumotlarini tahrirlash"""
    group = Group.query.get_or_404(group_id)
    
    # Only owner can edit group
    if not group.is_owner(current_user):
        flash('Faqat guruh egasi ma\'lumotlarni tahrirlashi mumkin', 'danger')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    form = EditGroupForm(obj=group)
    
    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        
        # Handle avatar update
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                # Delete old avatar
                if group.avatar and group.avatar != 'group_default.png':
                    delete_image(group.avatar, 'group_avatars')
                
                # Save new avatar
                filename = save_image(file, 'group_avatars')
                if filename:
                    group.avatar = filename
        
        db.session.commit()
        flash('Guruh ma\'lumotlari yangilandi', 'success')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    return render_template('groups/edit.html', form=form, group=group)

@groups_bp.route('/groups/<int:group_id>/delete', methods=['POST'])
@login_required
def delete_group(group_id):
    """Guruhni o'chirish"""
    group = Group.query.get_or_404(group_id)
    
    # Only owner can delete group
    if not group.is_owner(current_user):
        flash('Faqat guruh egasi guruhni o\'chira oladi', 'danger')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    # Delete all messages
    Message.query.filter_by(group_id=group_id).delete()
    
    # Delete all members
    GroupMember.query.filter_by(group_id=group_id).delete()
    
    # Delete group
    db.session.delete(group)
    db.session.commit()
    
    flash('Guruh o\'chirildi', 'success')
    return redirect(url_for('groups.list_groups'))

@groups_bp.route('/groups/<int:group_id>/invite')
@login_required
def invite_to_group(group_id):
    """Guruhga taklif qilish"""
    group = Group.query.get_or_404(group_id)
    
    # Check permissions
    member = GroupMember.query.filter_by(
        group_id=group_id, 
        user_id=current_user.id
    ).first()
    
    if not member or not member.is_admin():
        flash('Bu amal uchun ruxsat yo\'q', 'danger')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    return render_template('groups/invite.html', group=group)

@groups_bp.route('/groups/join/<invite_code>')
@login_required
def join_group(invite_code):
    """Taklif orqali guruhga qo'shilish"""
    group = Group.query.filter_by(invite_code=invite_code).first_or_404()
    
    # Check if already member
    existing_member = GroupMember.query.filter_by(
        group_id=group.id,
        user_id=current_user.id
    ).first()
    
    if existing_member:
        flash('Siz allaqachon bu guruh a\'zosisiz', 'info')
    else:
        # Add new member
        member = GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            role='member'
        )
        db.session.add(member)
        db.session.commit()
        
        flash(f'"{group.name}" guruhiga qo\'shildingiz!', 'success')
    
    return redirect(url_for('groups.view_group', group_id=group.id))

@groups_bp.route('/groups/<int:group_id>/members')
@login_required
def group_members(group_id):
    """Guruh a'zolarini ko'rish"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is member
    if not group.is_member(current_user):
        flash('Bu guruhga kirish uchun ruxsat yo\'q', 'danger')
        return redirect(url_for('groups.list_groups'))
    
    members = GroupMember.query.filter_by(group_id=group_id).all()
    
    return render_template('groups/members.html', group=group, members=members)

@groups_bp.route('/groups/<int:group_id>/members/<int:user_id>/role', methods=['POST'])
@login_required
def change_member_role(group_id, user_id):
    """A'zo rolini o'zgartirish"""
    group = Group.query.get_or_404(group_id)
    
    # Only owner can change roles
    if not group.is_owner(current_user):
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=user_id
    ).first_or_404()
    
    # Can't change owner's role
    if member.role == 'owner':
        return jsonify({'error': 'Guruh egasining rolini o\'zgartirib bo\'lmaydi'}), 400
    
    new_role = request.json.get('role')
    if new_role in ['admin', 'member']:
        member.role = new_role
        db.session.commit()
        return jsonify({'success': True, 'role': new_role})
    
    return jsonify({'error': 'Noto\'g\'ri rol'}), 400

@groups_bp.route('/groups/<int:group_id>/members/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_member(group_id, user_id):
    """A'zoni guruhdan chiqarish"""
    group = Group.query.get_or_404(group_id)
    
    # Check permissions
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    
    if not member or not member.is_admin():
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    target_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=user_id
    ).first_or_404()
    
    # Can't remove owner
    if target_member.role == 'owner':
        return jsonify({'error': 'Guruh egasini chiqarib bolmaydi'}), 400
    
    db.session.delete(target_member)
    db.session.commit()
    
    return jsonify({'success': True})

@groups_bp.route('/groups/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    """Guruhni tark etish"""
    group = Group.query.get_or_404(group_id)
    
    # Can't leave if you're the owner
    if group.is_owner(current_user):
        flash('Guruh egasi guruhni tark eta olmaydi. Avval boshqa egaga topshiring yoki guruhni o\'chiring.', 'danger')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    
    if member:
        db.session.delete(member)
        db.session.commit()
        flash(f'"{group.name}" guruhidan chiqdingiz', 'success')
    
    return redirect(url_for('groups.list_groups'))

@groups_bp.route('/groups/<int:group_id>/regenerate-invite', methods=['POST'])
@login_required
def regenerate_invite(group_id):
    """Yangi taklif kodini yaratish"""
    group = Group.query.get_or_404(group_id)
    
    # Only owner can regenerate invite code
    if not group.is_owner(current_user):
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    group.regenerate_invite_code()
    
    return jsonify({
        'success': True, 
        'invite_code': group.invite_code,
        'invite_url': url_for('groups.join_group', invite_code=group.invite_code, _external=True)
    })