from flask import Blueprint, request, jsonify
from models import Message
from extension import db
from models.user_cancel_stats import UserCancelStats

bp = Blueprint('message', __name__, url_prefix='/api/messages')

@bp.route('/', methods=['GET'])
def get_messages():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '缺少user_id'})
    msgs = Message.query.filter_by(user_id=user_id).order_by(Message.created_at.desc()).all()
    data = [
        {
            'id': m.id,
            'type': m.type,
            'content': m.content,
            'is_read': m.is_read,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'related_id': m.related_id
        }
        for m in msgs
    ]
    return jsonify({'success': True, 'data': data})

@bp.route('/<int:msg_id>/read', methods=['POST'])
def read_message(msg_id):
    msg = Message.query.get(msg_id)
    if not msg:
        return jsonify({'success': False, 'message': '消息不存在'})
    msg.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/user/<int:user_id>/cancelled-orders', methods=['GET'])
def get_cancelled_orders(user_id):
    stats = UserCancelStats.query.get(user_id)
    return jsonify({'success': True, 'cancelled_orders': stats.cancelled_orders if stats else 0}) 