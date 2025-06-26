from flask import Blueprint, request, jsonify
from models.game_character import GameCharacter, GameCharacterRating
from extension import db
from datetime import datetime
from models.game import Game

game_character_api = Blueprint('game_character_api', __name__, url_prefix='/api/game-character')

# 新增或更新评分
@game_character_api.route('/ratings', methods=['POST'])
def rate_character():
    data = request.get_json()
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    appearance_score = data.get('appearance_score')
    personality_score = data.get('personality_score')
    if not user_id or not character_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    rating = GameCharacterRating.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not rating:
        rating = GameCharacterRating(user_id=user_id, character_id=character_id)
        db.session.add(rating)
    if appearance_score is not None:
        rating.appearance_score = appearance_score
    if personality_score is not None:
        rating.personality_score = personality_score
    rating.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

# 查询某角色所有评分
@game_character_api.route('/ratings', methods=['GET'])
def get_character_ratings():
    character_id = request.args.get('character_id', type=int)
    if not character_id:
        return jsonify({'success': False, 'message': '缺少character_id'}), 400
    ratings = GameCharacterRating.query.filter_by(character_id=character_id).all()
    data = [
        {
            'user_id': r.user_id,
            'appearance_score': r.appearance_score,
            'personality_score': r.personality_score,
            'created_at': r.created_at,
            'updated_at': r.updated_at
        } for r in ratings
    ]
    return jsonify({'success': True, 'data': data})

# 查询某用户所有评分
@game_character_api.route('/ratings/user', methods=['GET'])
def get_user_ratings():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'success': False, 'message': '缺少user_id'}), 400
    ratings = GameCharacterRating.query.filter_by(user_id=user_id).all()
    data = [
        {
            'character_id': r.character_id,
            'appearance_score': r.appearance_score,
            'personality_score': r.personality_score,
            'created_at': r.created_at,
            'updated_at': r.updated_at
        } for r in ratings
    ]
    return jsonify({'success': True, 'data': data})

# 查询某角色的平均分
@game_character_api.route('/ratings/summary', methods=['GET'])
def get_character_rating_summary():
    character_id = request.args.get('character_id', type=int)
    if not character_id:
        return jsonify({'success': False, 'message': '缺少character_id'}), 400
    from sqlalchemy import func
    avg_appearance = db.session.query(func.avg(GameCharacterRating.appearance_score)).filter_by(character_id=character_id).scalar()
    avg_personality = db.session.query(func.avg(GameCharacterRating.personality_score)).filter_by(character_id=character_id).scalar()
    return jsonify({'success': True, 'appearance_avg': avg_appearance or 0, 'personality_avg': avg_personality or 0})

# 获取所有角色列表
@game_character_api.route('/list', methods=['GET'])
def get_character_list():
    characters = GameCharacter.query.all()
    # 批量查游戏名
    game_ids = list(set([c.game_id for c in characters]))
    games = {g.game_id: g.name for g in Game.query.filter(Game.game_id.in_(game_ids)).all()}
    data = [
        {
            'id': c.id,
            'name': c.name,
            'avatar': c.avatar,
            'cv': c.cv,
            'description': c.description,
            'role_type': c.role_type,
            'game_id': c.game_id,
            'game_name': games.get(c.game_id, '')
        } for c in characters
    ]
    return jsonify({'success': True, 'data': data}) 