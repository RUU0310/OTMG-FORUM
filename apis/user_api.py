from flask import Blueprint, request, jsonify, session, make_response
from models import User, Game
from extension import db
from flask_cors import cross_origin
from datetime import datetime

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
        'role': u.role,
        'upgrade_status': u.upgrade_status,
        'upgrade_request_time': u.upgrade_request_time
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
        'role': u.role,
        'upgrade_status': u.upgrade_status,
        'upgrade_request_time': u.upgrade_request_time
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
        role=data.get('role', 'user'),
        upgrade_status='none',
        upgrade_request_time=None
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({'user_id': u.user_id})

@user_bp.route('/users/register', methods=['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    nickname = data.get('nickname', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    
    # 验证必填字段
    if not username or not password:
        return jsonify({'status': 'fail', 'message': '用户名和密码不能为空'}), 400
    
    # 检查用户名唯一性
    if User.query.filter_by(username=username).first():
        return jsonify({'status': 'fail', 'message': '用户名已存在'}), 400
    
    # 检查邮箱唯一性（如果提供了邮箱）
    if email and User.query.filter_by(email=email).first():
        return jsonify({'status': 'fail', 'message': '邮箱已存在'}), 400
    
    # 检查手机号唯一性（如果提供了手机号）
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'status': 'fail', 'message': '手机号已存在'}), 400
    
    # 创建新用户
    new_user = User(
        username=username,
        password=password,
        nickname=nickname,
        email=email,
        phone=phone,
        avatar='',
        bio='',
        role='user',
        upgrade_status='none',
        upgrade_request_time=None
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # 设置session
        session['user_id'] = new_user.user_id
        session['role'] = new_user.role
        
        return jsonify({
            'status': 'success',
            'user_id': new_user.user_id,
            'username': new_user.username,
            'role': new_user.role,
            'nickname': new_user.nickname,
            'upgrade_status': new_user.upgrade_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'fail', 'message': '注册失败，请稍后重试'}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    data = request.json
    for field in ['username', 'password', 'nickname', 'phone', 'email', 'avatar', 'bio', 'role', 'upgrade_status', 'upgrade_request_time']:
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

@user_bp.route('/users/<int:user_id>/upgrade', methods=['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def upgrade_user_role(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    
    # 检查当前用户是否为普通用户
    if u.role != 'user':
        return jsonify({'status': 'fail', 'message': '只有普通用户可以申请升级为发行商'}), 400
    
    # 检查是否已有待审核的申请
    if u.upgrade_status == 'pending':
        return jsonify({'status': 'fail', 'message': '您已有待审核的升级申请，请耐心等待'}), 400
    
    # 提交升级申请
    u.upgrade_status = 'pending'
    u.upgrade_request_time = datetime.now().isoformat()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '升级申请已提交，请等待管理员审核',
        'upgrade_status': 'pending'
    })

@user_bp.route('/users/upgrade-requests', methods=['GET'])
def get_upgrade_requests():
    """获取所有待审核的升级申请（管理员专用）"""
    pending_users = User.query.filter_by(upgrade_status='pending').all()
    
    return jsonify({
        'status': 'success',
        'requests': [{
            'user_id': u.user_id,
            'username': u.username,
            'nickname': u.nickname,
            'phone': u.phone,
            'email': u.email,
            'avatar': u.avatar,
            'bio': u.bio,
            'role': u.role,
            'upgrade_status': u.upgrade_status,
            'upgrade_request_time': u.upgrade_request_time
        } for u in pending_users]
    })

@user_bp.route('/users/<int:user_id>/upgrade-review', methods=['POST'])
def review_upgrade_request(user_id):
    """审核升级申请（管理员专用）"""
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.json
    action = data.get('action')  # 'approve' 或 'reject'
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': '无效的操作'}), 400
    
    if u.upgrade_status != 'pending':
        return jsonify({'error': '该申请已被处理'}), 400
    
    if action == 'approve':
        u.role = 'publisher'
        u.upgrade_status = 'approved'
        message = '升级申请已通过'
    else:
        u.upgrade_status = 'rejected'
        message = '升级申请已被拒绝'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': message,
        'new_role': u.role,
        'upgrade_status': u.upgrade_status
    })

@user_bp.route('/users/<int:user_id>/published-games', methods=['GET'])
def get_user_published_games(user_id):
    """获取发行商发布的游戏"""
    try:
        # 检查用户是否存在且为发行商
        user = User.query.get(user_id)
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        
        if user.role != 'publisher':
            return jsonify({'status': 'error', 'message': '只有发行商可以查看发布游戏'}), 403
        
        # 获取该发行商发布的游戏（通过publisher字段匹配昵称或用户名）
        publisher_name = user.nickname or user.username
        games = Game.query.filter_by(publisher=publisher_name).all()
        
        results = []
        for game in games:
            results.append({
                'game_id': game.game_id,
                'name': game.name,
                'image_url': game.image_url,
                'description': game.description,
                'region': game.region,
                'publisher': game.publisher,
                'release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
                'purchase_link': game.purchase_link,
                'is_official': game.is_official,
                'created_at': game.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(game, 'created_at') and game.created_at else None
            })
        
        return jsonify({
            'status': 'success',
            'games': results
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
        'nickname': user.nickname,
        'upgrade_status': user.upgrade_status
    })
