from flask import Blueprint, request, jsonify
from models import Game
from extension import db
from datetime import datetime
from models.game_user import GameUser
from models.user import User
from flask import session
from models.game_comment import GameComment
from models.game_comment_like import GameCommentLike
from models.game_character import GameCharacter
from models.group_post import Group

game_bp = Blueprint('game', __name__)

# 你可以把原先的GameApi的所有方法拆成单独的函数
@game_bp.route('/games', methods=['GET'])
def get_games():
    games = Game.query.all()
    results = [
        {
            'game_id': game.game_id,
            'name': game.name,
            'image_url': game.image_url,
            'description': game.description,
            'region': game.region,
            'publisher': game.publisher,
            'release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
            'purchase_link': game.purchase_link,
        } for game in games
    ]
    return jsonify({'status': 'success', 'results': results})

@game_bp.route('/games', methods=['POST'])
def add_game():
    form = request.json
    game = Game(
        name=form.get('name'),
        image_url=form.get('image_url'),
        description=form.get('description'),
        region=form.get('region'),
        publisher=form.get('publisher'),
        release_date=datetime.strptime(form.get('release_date'), '%Y-%m-%d').date() if form.get('release_date') else None,
        purchase_link=form.get('purchase_link'),
        created_at=datetime.utcnow()
    )
    db.session.add(game)
    db.session.commit()
    # 自动为新游戏创建小组（避免重复）
    if not Group.query.filter_by(game_id=game.game_id).first():
        group = Group(game_id=game.game_id, name=game.name + "小组", description=f"{game.name} 讨论小组")
        db.session.add(group)
        db.session.commit()
    return jsonify({'status': 'success', 'game_id': game.game_id})

@game_bp.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
    form = request.json
    for field in ['name', 'image_url', 'description', 'region', 'publisher', 'purchase_link']:
        if field in form:
            setattr(game, field, form[field])
    # 单独处理 release_date
    if 'release_date' in form and form['release_date']:
        try:
            game.release_date = datetime.strptime(form['release_date'], '%Y-%m-%d').date()
        except Exception:
            return jsonify({'status': 'error', 'message': '日期格式错误'}), 400
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
    db.session.delete(game)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game_detail(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
    result = {
        'game_id': game.game_id,
        'name': game.name,
        'image_url': game.image_url,
        'description': game.description,
        'region': game.region,
        'publisher': game.publisher,
        'release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
        'purchase_link': game.purchase_link,
        'created_at': game.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(game, 'created_at') and game.created_at else None
    }
    return jsonify({'status': 'success', 'result': result})

@game_bp.route('/games/<int:game_id>/user_status', methods=['GET'])
def get_user_game_status(game_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    gu = GameUser.query.filter_by(user_id=user_id, game_id=game_id).first()
    if not gu:
        return jsonify({'status': 'success', 'result': None})
    return jsonify({'status': 'success', 'result': {'status': gu.status, 'rating': gu.rating}})

@game_bp.route('/games/<int:game_id>/user_status', methods=['POST'])
def set_user_game_status(game_id):
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    status = data.get('status')
    rating = data.get('rating')
    gu = GameUser.query.filter_by(user_id=user_id, game_id=game_id).first()
    if not gu:
        gu = GameUser(user_id=user_id, game_id=game_id)
        db.session.add(gu)
    if status:
        gu.status = status
    if rating is not None:
        if rating == '' or rating is None:
            gu.rating = None
        else:
            gu.rating = float(rating)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>/stats', methods=['GET'])
def get_game_stats(game_id):
    wish_count = GameUser.query.filter_by(game_id=game_id, status='wish').count()
    playing_count = GameUser.query.filter_by(game_id=game_id, status='playing').count()
    played_count = GameUser.query.filter_by(game_id=game_id, status='played').count()
    ratings = [gu.rating for gu in GameUser.query.filter(GameUser.game_id==game_id, GameUser.rating!=None).all()]
    avg_rating = round(sum(ratings)/len(ratings), 2) if ratings else None
    return jsonify({
        'status': 'success',
        'result': {
            'wish': wish_count,
            'playing': playing_count,
            'played': played_count,
            'avg_rating': avg_rating,
            'rating_count': len(ratings)
        }
    })

@game_bp.route('/games/<int:game_id>/comments', methods=['GET'])
def get_game_comments(game_id):
    user_id = request.args.get('user_id', type=int)
    comments = GameComment.query.filter_by(game_id=game_id).order_by(GameComment.created_at.desc()).all()
    result = []
    for c in comments:
        user = User.query.get(c.user_id)
        like_count = GameCommentLike.query.filter_by(comment_id=c.id).count()
        liked = False
        if user_id:
            liked = GameCommentLike.query.filter_by(comment_id=c.id, user_id=user_id).first() is not None
        # 获取评论用户对该游戏的评分
        user_game = GameUser.query.filter_by(user_id=c.user_id, game_id=game_id).first()
        user_rating = user_game.rating if user_game and user_game.rating else None
        result.append({
            'id': c.id,
            'user_id': c.user_id,
            'nickname': user.nickname if user else '',
            'avatar': user.avatar if user else '',
            'content': c.content,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
            'like_count': like_count,
            'liked': liked,
            'user_rating': user_rating
        })
    return jsonify({'status': 'success', 'results': result})

@game_bp.route('/games/<int:game_id>/comments', methods=['POST'])
def add_game_comment(game_id):
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content', '').strip()
    if not user_id or not content:
        return jsonify({'status': 'error', 'message': '缺少用户或内容'}), 400
    comment = GameComment(game_id=game_id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>/comments/<int:comment_id>/like', methods=['POST'])
def like_game_comment(game_id, comment_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    like = GameCommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        db.session.add(GameCommentLike(user_id=user_id, comment_id=comment_id))
        db.session.commit()
        liked = True
    like_count = GameCommentLike.query.filter_by(comment_id=comment_id).count()
    return jsonify({'status': 'success', 'like_count': like_count, 'liked': liked})

@game_bp.route('/games/<int:game_id>/comments/<int:comment_id>', methods=['PUT'])
def edit_game_comment(game_id, comment_id):
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content', '').strip()
    comment = GameComment.query.filter_by(id=comment_id, game_id=game_id, user_id=user_id).first()
    if not comment:
        return jsonify({'status': 'error', 'message': '评论不存在或无权限'}), 403
    if not content:
        return jsonify({'status': 'error', 'message': '内容不能为空'}), 400
    comment.content = content
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_game_comment(game_id, comment_id):
    user_id = request.args.get('user_id', type=int)
    comment = GameComment.query.filter_by(id=comment_id, game_id=game_id, user_id=user_id).first()
    if not comment:
        return jsonify({'status': 'error', 'message': '评论不存在或无权限'}), 403
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'status': 'success'})

# 角色：增
@game_bp.route('/games/<int:game_id>/characters', methods=['POST'])
def add_character(game_id):
    data = request.json
    char = GameCharacter(
        game_id=game_id,
        name=data.get('name'),
        cv=data.get('cv'),
        avatar=data.get('avatar'),
        description=data.get('description'),
        extra_info=data.get('extra_info'),
        role_type=data.get('role_type', '可攻略')
    )
    db.session.add(char)
    db.session.commit()
    return jsonify({'status': 'success', 'id': char.id})

# 角色：查（列表）
@game_bp.route('/games/<int:game_id>/characters', methods=['GET'])
def get_characters(game_id):
    chars = GameCharacter.query.filter_by(game_id=game_id).all()
    results = []
    for c in chars:
        results.append({
            'id': c.id,
            'game_id': c.game_id,
            'name': c.name,
            'cv': c.cv,
            'avatar': c.avatar,
            'description': c.description,
            'extra_info': c.extra_info,
            'role_type': c.role_type
        })
    return jsonify({'status': 'success', 'results': results})

# 角色：查（单个）
@game_bp.route('/characters/<int:char_id>', methods=['GET'])
def get_character(char_id):
    c = GameCharacter.query.get(char_id)
    if not c:
        return jsonify({'status': 'error', 'message': '角色不存在'}), 404
    return jsonify({'status': 'success', 'result': {
        'id': c.id,
        'game_id': c.game_id,
        'name': c.name,
        'cv': c.cv,
        'avatar': c.avatar,
        'description': c.description,
        'extra_info': c.extra_info,
        'role_type': c.role_type
    }})

# 角色：改
@game_bp.route('/characters/<int:char_id>', methods=['PUT'])
def update_character(char_id):
    c = GameCharacter.query.get(char_id)
    if not c:
        return jsonify({'status': 'error', 'message': '角色不存在'}), 404
    data = request.json
    for field in ['name', 'cv', 'avatar', 'description', 'extra_info', 'role_type']:
        if field in data:
            setattr(c, field, data[field])
    db.session.commit()
    return jsonify({'status': 'success'})

# 角色：删
@game_bp.route('/characters/<int:char_id>', methods=['DELETE'])
def delete_character(char_id):
    c = GameCharacter.query.get(char_id)
    if not c:
        return jsonify({'status': 'error', 'message': '角色不存在'}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/users/<int:user_id>/game-status', methods=['GET'])
def get_user_game_status_list(user_id):
    """获取用户的所有游戏状态"""
    try:
        # 获取用户的所有游戏状态
        game_users = GameUser.query.filter_by(user_id=user_id).all()
        
        # 获取所有游戏信息
        games = Game.query.all()
        game_map = {game.game_id: game for game in games}
        
        # 按状态分类
        wish_games = []
        playing_games = []
        played_games = []
        
        for gu in game_users:
            game = game_map.get(gu.game_id)
            if not game:
                continue
                
            game_info = {
                'game_id': game.game_id,
                'name': game.name,
                'image_url': game.image_url,
                'publisher': game.publisher,
                'rating': gu.rating
            }
            
            if gu.status == 'wish':
                wish_games.append(game_info)
            elif gu.status == 'playing':
                playing_games.append(game_info)
            elif gu.status == 'played':
                played_games.append(game_info)
        
        return jsonify({
            'status': 'success',
            'game_status': {
                'wish': wish_games,
                'playing': playing_games,
                'played': played_games
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500