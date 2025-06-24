from flask import Blueprint, request, jsonify, session, make_response
from models import User
from extension import db
from flask_cors import cross_origin

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'user_id': u.user_id,
        'username': u.username,
        'nickname': u.nickname,
        'phone': u.phone,
        'email': u.email,
        'avatar': u.avatar,
        'bio': u.bio,
        'role': u.role
    } for u in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({
        'user_id': u.user_id,
        'username': u.username,
        'nickname': u.nickname,
        'phone': u.phone,
        'email': u.email,
        'avatar': u.avatar,
        'bio': u.bio,
        'role': u.role
    })

@user_bp.route('/users', methods=['POST'])
def add_user():
    data = request.json
    # 检查用户名、邮箱、手机号唯一性
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'status': 'fail', 'message': '用户名已存在'}), 400
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'fail', 'message': '邮箱已存在'}), 400
    if data.get('phone') and User.query.filter_by(phone=data['phone']).first():
        return jsonify({'status': 'fail', 'message': '手机号已存在'}), 400

    u = User(
        username=data['username'],
        password=data['password'],
        nickname=data.get('nickname', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        avatar=data.get('avatar', ''),
        bio=data.get('bio', ''),
        role=data.get('role', 'user')
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({'user_id': u.user_id})

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    data = request.json
    for field in ['username', 'password', 'nickname', 'phone', 'email', 'avatar', 'bio', 'role']:
        if field in data:
            setattr(u, field, data[field])
    db.session.commit()
    return jsonify({'msg': '更新成功'})

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    db.session.delete(u)
    db.session.commit()
    return jsonify({'msg': '删除成功'})

@user_bp.route('/login', methods=['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'status': 'fail', 'message': '用户名或密码错误'}), 401
    session['user_id'] = user.user_id
    session['role'] = user.role
    return jsonify({
        'status': 'success',
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'nickname': user.nickname
    })
