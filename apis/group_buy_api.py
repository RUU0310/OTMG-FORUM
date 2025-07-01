from flask import Blueprint, request, jsonify
from models.group_buy import (
    GroupBuyProduct, GroupBuyCharacter, GroupBuy, GroupBuyMember, GroupBuyCharacterAdjustment, UserGroupBuyStats, GroupBuyRequest
)
from models.user import User
from models import Message
from extension import db
from datetime import datetime
from models.user_cancel_stats import UserCancelStats

group_buy_api = Blueprint('group_buy_api', __name__)

# ==================== 商品管理接口 ====================

@group_buy_api.route('/products', methods=['GET'])
def get_products():
    """获取所有商品列表（含角色）"""
    try:
        products = GroupBuyProduct.query.all()
        result = []
        for product in products:
            characters = GroupBuyCharacter.query.filter_by(product_id=product.product_id).all()
            character_list = [
                {
                    'character_id': char.character_id,
                    'name': char.name,
                    'image': char.image,
                    'is_popular': char.is_popular
                } for char in characters
            ]
            result.append({
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'image': product.image,
                'characters': character_list
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/products', methods=['POST'])
def create_product():
    """创建新商品（带角色）"""
    try:
        data = request.get_json()
        product = GroupBuyProduct(
            name=data['name'],
            description=data.get('description', ''),
            image=data.get('image', '')
        )
        db.session.add(product)
        db.session.flush()  # 获取product_id
        for char in data.get('characters', []):
            db.session.add(GroupBuyCharacter(
                product_id=product.product_id,
                name=char['name'],
                image=char.get('image', ''),
                is_popular=char.get('is_popular', False)
            ))
        db.session.commit()
        return jsonify({'success': True, 'product_id': product.product_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取单个商品详情（带角色）"""
    try:
        product = GroupBuyProduct.query.get_or_404(product_id)
        characters = GroupBuyCharacter.query.filter_by(product_id=product_id).all()
        character_list = [
            {
                'character_id': char.character_id,
                'name': char.name,
                'image': char.image,
                'is_popular': char.is_popular
            } for char in characters
        ]
        return jsonify({
            'success': True,
            'data': {
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'image': product.image,
                'characters': character_list
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 拼团管理接口 ====================

@group_buy_api.route('/group-buys', methods=['GET'])
def get_group_buys():
    """获取拼团列表"""
    try:
        status = request.args.get('status', None)
        query = GroupBuy.query
        if status:
            query = query.filter_by(status=status)
        group_buys = query.order_by(GroupBuy.created_at.desc()).all()
        result = []
        for group_buy in group_buys:
            leader = User.query.get(group_buy.leader_id)
            product = GroupBuyProduct.query.get(group_buy.product_id)
            # 获取角色数量
            characters = GroupBuyCharacter.query.filter_by(product_id=product.product_id).all() if product else []
            member_count = GroupBuyMember.query.filter_by(group_buy_id=group_buy.group_buy_id).count()
            # 获取拼团角色可拼团总数
            adjustments = GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_buy.group_buy_id).all()
            total_max_count = sum([adj.max_count for adj in adjustments])
            # 自动调整状态
            all_full = True
            for adj in adjustments:
                used = GroupBuyMember.query.filter_by(group_buy_id=group_buy.group_buy_id, character_id=adj.character_id).count()
                if used < adj.max_count:
                    all_full = False
                    break
            if group_buy.status == 'recruiting' and all_full:
                group_buy.status = 'full'
                db.session.commit()
            elif group_buy.status == 'full' and not all_full:
                group_buy.status = 'recruiting'
                db.session.commit()
            result.append({
                'group_buy_id': group_buy.group_buy_id,
                'title': group_buy.title,
                'description': group_buy.description,
                'status': group_buy.status,
                'deadline': group_buy.deadline.isoformat() if group_buy.deadline else None,
                'created_at': group_buy.created_at.isoformat() if group_buy.created_at else None,
                'leader': {
                    'user_id': leader.user_id,
                    'username': leader.username,
                    'nickname': leader.nickname
                } if leader else None,
                'product': {
                    'product_id': product.product_id,
                    'name': product.name,
                    'image': product.image,
                    'characters': [
                        {'character_id': c.character_id, 'name': c.name, 'image': c.image, 'is_popular': c.is_popular}
                        for c in characters
                    ]
                } if product else None,
                'member_count': member_count,
                'average_price': float(group_buy.average_price) if group_buy.average_price is not None else None,
                'total_max_count': total_max_count
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/group-buys', methods=['POST'])
def create_group_buy():
    """创建拼团（带角色调价和可拼团个数）"""
    try:
        data = request.get_json()
        group_buy = GroupBuy(
            product_id=data['product_id'],
            leader_id=data['leader_id'],
            title=data['title'],
            description=data.get('description', ''),
            contact_info=data.get('contact_info', ''),
            average_price=data['average_price'],
            status='recruiting',
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None
        )
        db.session.add(group_buy)
        db.session.flush()  # 获取group_buy_id
        for adj in data.get('character_adjustments', []):
            db.session.add(GroupBuyCharacterAdjustment(
                group_buy_id=group_buy.group_buy_id,
                character_id=adj['character_id'],
                price_adjustment=adj.get('price_adjustment', 0),
                max_count=adj.get('max_count', 1)
            ))
        db.session.commit()
        return jsonify({'success': True, 'group_buy_id': group_buy.group_buy_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/group-buys/<int:group_buy_id>/join', methods=['POST'])
def join_group_buy(group_buy_id):
    """
    用户参与拼团，选择角色，可多次多份参与
    body: { user_id, character_id, count }
    """
    data = request.get_json()
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    count = int(data.get('count', 1))
    if not user_id or not character_id or count < 1:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    # 校验角色剩余
    adjustment = GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_buy_id, character_id=character_id).first()
    if not adjustment or adjustment.max_count <= 0:
        return jsonify({'success': False, 'message': '该角色已无可拼团名额'}), 400

    # 已有该角色人数
    used_count = GroupBuyMember.query.filter_by(group_buy_id=group_buy_id, character_id=character_id).count()
    remain = adjustment.max_count - used_count
    if remain < count:
        return jsonify({'success': False, 'message': f'剩余名额不足，仅剩{remain}份'}), 400

    # 价格
    group_buy = GroupBuy.query.get_or_404(group_buy_id)
    final_price = float(group_buy.average_price) + float(adjustment.price_adjustment or 0)

    for _ in range(count):
        member = GroupBuyMember(
            group_buy_id=group_buy_id,
            user_id=user_id,
            character_id=character_id,
            final_price=final_price,
            status='approved'
        )
        db.session.add(member)
    db.session.flush()
    # 检查是否所有角色都满员
    adjustments = GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_buy_id).all()
    all_full = True
    for adj in adjustments:
        used = GroupBuyMember.query.filter_by(group_buy_id=group_buy_id, character_id=adj.character_id).count()
        if used < adj.max_count:
            all_full = False
            break
    if all_full:
        group_buy.status = 'full'
    db.session.commit()
    return jsonify({'success': True, 'message': f'成功参与{count}份'})

@group_buy_api.route('/group-buys/<int:group_buy_id>', methods=['GET'])
def get_group_buy(group_buy_id):
    """获取拼团详情（带角色调价和可拼团个数）"""
    try:
        group_buy = GroupBuy.query.get_or_404(group_buy_id)
        product = GroupBuyProduct.query.get(group_buy.product_id)
        leader = User.query.get(group_buy.leader_id)
        characters = GroupBuyCharacter.query.filter_by(product_id=product.product_id).all()
        adjustments = {adj.character_id: {'price_adjustment': float(adj.price_adjustment), 'max_count': adj.max_count} for adj in GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_buy_id).all()}
        # 统计每个角色已参与人数
        joined_counts = {c.character_id: GroupBuyMember.query.filter_by(group_buy_id=group_buy_id, character_id=c.character_id).count() for c in characters}
        character_list = []
        all_full = True
        for char in characters:
            adj = adjustments.get(char.character_id, {'price_adjustment': 0, 'max_count': 1})
            joined = joined_counts.get(char.character_id, 0)
            if joined < adj['max_count']:
                all_full = False
            character_list.append({
                'character_id': char.character_id,
                'name': char.name,
                'image': char.image,
                'is_popular': char.is_popular,
                'price_adjustment': adj['price_adjustment'],
                'max_count': adj['max_count'],
                'joined_count': joined
            })
        # 自动调整状态
        if group_buy.status == 'recruiting':
            if all_full:
                group_buy.status = 'full'
                db.session.commit()
            else:
                group_buy.status = 'recruiting'
        # 返回成员明细
        members = [
            {
                'user_id': m.user_id,
                'character_id': m.character_id,
                'joined_at': m.joined_at.isoformat() if m.joined_at else None
            }
            for m in GroupBuyMember.query.filter_by(group_buy_id=group_buy_id).all()
        ]
        return jsonify({
            'success': True,
            'data': {
                'group_buy_id': group_buy.group_buy_id,
                'title': group_buy.title,
                'description': group_buy.description,
                'contact_info': group_buy.contact_info,
                'average_price': float(group_buy.average_price),
                'deadline': group_buy.deadline.isoformat() if group_buy.deadline else None,
                'status': group_buy.status,
                'leader': {
                    'user_id': leader.user_id,
                    'username': leader.username,
                    'nickname': leader.nickname
                } if leader else None,
                'product': {
                    'product_id': product.product_id,
                    'name': product.name,
                    'description': product.description,
                    'image': product.image
                },
                'characters': character_list,
                'members': members
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/group-buys/<int:group_buy_id>', methods=['PUT', 'PATCH'])
def update_group_buy(group_buy_id):
    """编辑拼团（仅团长可编辑）"""
    try:
        group_buy = GroupBuy.query.get_or_404(group_buy_id)
        data = request.get_json()
        # 权限校验：仅团长可编辑
        user_id = data.get('user_id')
        if not user_id or group_buy.leader_id != user_id:
            return jsonify({'success': False, 'message': '无权限操作'}), 403

        # 可编辑字段
        for field in ['title', 'description', 'contact_info', 'average_price', 'deadline', 'status']:
            if field in data:
                # 只在首次变更为completed时+1
                if field == 'status' and data[field] == 'completed' and group_buy.status != 'completed':
                    stats = UserGroupBuyStats.query.filter_by(user_id=group_buy.leader_id).first()
                    if stats:
                        stats.successful_groups += 1
                setattr(group_buy, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': '拼团信息已更新'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/group-buys/<int:group_buy_id>/cancel', methods=['POST'])
def cancel_group_buy_member(group_buy_id):
    """
    用户取消参与拼团
    body: { user_id, character_id, count }
    """
    data = request.get_json()
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    count = int(data.get('count', 1))
    if not user_id or not character_id or count < 1:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    # 找到该用户参与的记录，按加入时间排序，删除count条
    members = GroupBuyMember.query.filter_by(
        group_buy_id=group_buy_id,
        user_id=user_id,
        character_id=character_id
    ).order_by(GroupBuyMember.joined_at.asc()).limit(count).all()
    if not members or len(members) < count:
        return jsonify({'success': False, 'message': '没有足够的可取消份数'}), 400

    for m in members:
        db.session.delete(m)

    # 更新用户拼团统计
    stats = UserGroupBuyStats.query.filter_by(user_id=user_id).first()
    if stats:
        stats.total_participated = max(0, stats.total_participated - count)
        stats.cancelled_orders += count

    # 新增：更新 user_cancel_stats
    cancel_stats = UserCancelStats.query.get(user_id)
    if not cancel_stats:
        cancel_stats = UserCancelStats(user_id=user_id, cancelled_orders=count)
        db.session.add(cancel_stats)
    else:
        cancel_stats.cancelled_orders += count

    db.session.commit()
    return jsonify({'success': True, 'message': f'成功取消{count}份'})

@group_buy_api.route('/user-group-buy-stats/<int:user_id>', methods=['GET'])
def get_user_group_buy_stats(user_id):
    # 实时统计该用户作为团长，状态为completed的拼团数
    count = GroupBuy.query.filter_by(leader_id=user_id, status='completed').count()
    return jsonify({
        'user_id': user_id,
        'successful_groups': count
    })

# 用户申请拼团
@group_buy_api.route('/group-buys/<int:group_buy_id>/request', methods=['POST'])
def request_group_buy(group_buy_id):
    data = request.get_json()
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    count = int(data.get('count', 1))
    message = data.get('message', '')
    if not user_id or not character_id or count < 1:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    # 校验是否已申请且未审核
    exist = GroupBuyRequest.query.filter_by(group_buy_id=group_buy_id, user_id=user_id, character_id=character_id, status='pending').first()
    if exist:
        return jsonify({'success': False, 'message': '你已申请该拼团该角色，待团长审核'}), 400
    req = GroupBuyRequest(
        group_buy_id=group_buy_id,
        user_id=user_id,
        character_id=character_id,
        count=count,
        message=message
    )
    db.session.add(req)
    db.session.commit()
    return jsonify({'success': True, 'message': '申请已提交，等待团长审核'})

# 团长查看待审核申请
@group_buy_api.route('/group-buys/requests', methods=['GET'])
def get_group_buy_requests():
    leader_id = request.args.get('leader_id', type=int)
    status = request.args.get('status', 'pending')
    query = GroupBuyRequest.query.join(GroupBuy, GroupBuyRequest.group_buy_id == GroupBuy.group_buy_id)
    if leader_id:
        query = query.filter(GroupBuy.leader_id == leader_id)
    if status:
        query = query.filter(GroupBuyRequest.status == status)
    requests = query.order_by(GroupBuyRequest.created_at.desc()).all()
    result = []
    for req in requests:
        user = User.query.get(req.user_id)
        group_buy = GroupBuy.query.get(req.group_buy_id)
        character = GroupBuyCharacter.query.get(req.character_id)
        result.append({
            'id': req.id,
            'group_buy_id': req.group_buy_id,
            'group_buy_title': group_buy.title if group_buy else '',
            'user_id': req.user_id,
            'username': user.username if user else '',
            'nickname': user.nickname if user else '',
            'character_id': req.character_id,
            'character_name': character.name if character else '',
            'count': req.count,
            'status': req.status,
            'message': req.message,
            'created_at': req.created_at.isoformat() if req.created_at else '',
            'reviewed_at': req.reviewed_at.isoformat() if req.reviewed_at else '',
        })
    return jsonify({'success': True, 'data': result})

# 团长审核申请
@group_buy_api.route('/group-buys/requests/<int:request_id>/review', methods=['POST'])
def review_group_buy_request(request_id):
    data = request.get_json()
    reviewer_id = data.get('reviewer_id')
    approve = data.get('approve')  # True/False
    group_request = GroupBuyRequest.query.get_or_404(request_id)
    group_buy = GroupBuy.query.get(group_request.group_buy_id)
    if not group_buy or group_buy.leader_id != reviewer_id:
        return jsonify({'success': False, 'message': '无权限操作'}), 403
    if group_request.status != 'pending':
        return jsonify({'success': False, 'message': '该申请已审核'}), 400
    group_request.status = 'approved' if approve else 'rejected'
    group_request.reviewed_at = datetime.utcnow()
    group_request.reviewer_id = reviewer_id
    if approve:
        # 审核通过，插入拼团成员
        adjustment = GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_request.group_buy_id, character_id=group_request.character_id).first()
        used_count = GroupBuyMember.query.filter_by(group_buy_id=group_request.group_buy_id, character_id=group_request.character_id).count()
        remain = adjustment.max_count - used_count
        if remain < group_request.count:
            db.session.commit()
            return jsonify({'success': False, 'message': f'剩余名额不足，仅剩{remain}份'}), 400
        group_buy = GroupBuy.query.get(group_request.group_buy_id)
        final_price = float(group_buy.average_price) + float(adjustment.price_adjustment or 0)
        for _ in range(group_request.count):
            member = GroupBuyMember(
                group_buy_id=group_request.group_buy_id,
                user_id=group_request.user_id,
                character_id=group_request.character_id,
                final_price=final_price,
                status='approved'
            )
            db.session.add(member)
    db.session.commit()
    applicant_id = group_request.user_id
    content = f"你申请参与拼团《{group_buy.title if group_buy else ''}》已被团长{'同意' if approve else '拒绝'}。"
    msg = Message(
        user_id=applicant_id,
        type='group_buy_review',
        content=content,
        is_read=False,
        created_at=datetime.utcnow(),
        related_id=request_id
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True, 'message': '审核完成'})

@group_buy_api.route('/users/<int:user_id>/my-group-buys', methods=['GET'])
def get_my_group_buys(user_id):
    """获取我发起的拼团列表（团长）"""
    try:
        status = request.args.get('status', None)
        query = GroupBuy.query.filter_by(leader_id=user_id)
        if status:
            query = query.filter_by(status=status)
        group_buys = query.order_by(GroupBuy.created_at.desc()).all()
        result = []
        for group_buy in group_buys:
            leader = User.query.get(group_buy.leader_id)
            product = GroupBuyProduct.query.get(group_buy.product_id)
            characters = GroupBuyCharacter.query.filter_by(product_id=product.product_id).all() if product else []
            member_count = GroupBuyMember.query.filter_by(group_buy_id=group_buy.group_buy_id).count()
            adjustments = GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_buy.group_buy_id).all()
            total_max_count = sum([adj.max_count for adj in adjustments])
            all_full = True
            for adj in adjustments:
                used = GroupBuyMember.query.filter_by(group_buy_id=group_buy.group_buy_id, character_id=adj.character_id).count()
                if used < adj.max_count:
                    all_full = False
                    break
            if group_buy.status == 'recruiting' and all_full:
                group_buy.status = 'full'
                db.session.commit()
            elif group_buy.status == 'full' and not all_full:
                group_buy.status = 'recruiting'
                db.session.commit()
            result.append({
                'group_buy_id': group_buy.group_buy_id,
                'title': group_buy.title,
                'description': group_buy.description,
                'status': group_buy.status,
                'deadline': group_buy.deadline.isoformat() if group_buy.deadline else None,
                'created_at': group_buy.created_at.isoformat() if group_buy.created_at else None,
                'leader': {
                    'user_id': leader.user_id,
                    'username': leader.username,
                    'nickname': leader.nickname
                } if leader else None,
                'product': {
                    'product_id': product.product_id,
                    'name': product.name,
                    'image': product.image,
                    'characters': [
                        {'character_id': c.character_id, 'name': c.name, 'image': c.image, 'is_popular': c.is_popular}
                        for c in characters
                    ]
                } if product else None,
                'member_count': member_count,
                'average_price': float(group_buy.average_price) if group_buy.average_price is not None else None,
                'total_max_count': total_max_count
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@group_buy_api.route('/users/<int:user_id>/joined-group-buys', methods=['GET'])
def get_joined_group_buys(user_id):
    """获取我参与的拼团列表（成员）"""
    try:
        # 找到该用户参与的所有拼团ID（去重）
        group_buy_ids = db.session.query(GroupBuyMember.group_buy_id).filter_by(user_id=user_id).distinct()
        group_buys = GroupBuy.query.filter(GroupBuy.group_buy_id.in_(group_buy_ids)).order_by(GroupBuy.created_at.desc()).all()
        result = []
        for group_buy in group_buys:
            leader = User.query.get(group_buy.leader_id)
            product = GroupBuyProduct.query.get(group_buy.product_id)
            characters = GroupBuyCharacter.query.filter_by(product_id=product.product_id).all() if product else []
            member_count = GroupBuyMember.query.filter_by(group_buy_id=group_buy.group_buy_id).count()
            adjustments = GroupBuyCharacterAdjustment.query.filter_by(group_buy_id=group_buy.group_buy_id).all()
            total_max_count = sum([adj.max_count for adj in adjustments])
            all_full = True
            for adj in adjustments:
                used = GroupBuyMember.query.filter_by(group_buy_id=group_buy.group_buy_id, character_id=adj.character_id).count()
                if used < adj.max_count:
                    all_full = False
                    break
            if group_buy.status == 'recruiting' and all_full:
                group_buy.status = 'full'
                db.session.commit()
            elif group_buy.status == 'full' and not all_full:
                group_buy.status = 'recruiting'
                db.session.commit()
            result.append({
                'group_buy_id': group_buy.group_buy_id,
                'title': group_buy.title,
                'description': group_buy.description,
                'status': group_buy.status,
                'deadline': group_buy.deadline.isoformat() if group_buy.deadline else None,
                'created_at': group_buy.created_at.isoformat() if group_buy.created_at else None,
                'leader': {
                    'user_id': leader.user_id,
                    'username': leader.username,
                    'nickname': leader.nickname
                } if leader else None,
                'product': {
                    'product_id': product.product_id,
                    'name': product.name,
                    'image': product.image,
                    'characters': [
                        {'character_id': c.character_id, 'name': c.name, 'image': c.image, 'is_popular': c.is_popular}
                        for c in characters
                    ]
                } if product else None,
                'member_count': member_count,
                'average_price': float(group_buy.average_price) if group_buy.average_price is not None else None,
                'total_max_count': total_max_count
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500 