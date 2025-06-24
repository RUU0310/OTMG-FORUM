from flask import Blueprint, request, jsonify
from models import Game
from extension import db
from datetime import datetime

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
