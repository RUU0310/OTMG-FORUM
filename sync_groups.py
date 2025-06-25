from models.game import Game
from models.group_post import Group
from extension import db
from app import app

# 使用Flask app上下文
with app.app_context():
    games = Game.query.all()
    count = 0
    for game in games:
        group = Group.query.filter_by(game_id=game.game_id).first()
        if not group:
            new_group = Group(
                game_id=game.game_id,
                name=game.name + "小组",
                description=game.description or f"{game.name} 的讨论小组"
            )
            db.session.add(new_group)
            count += 1
    db.session.commit()
    print(f"同步完成！新增小组 {count} 个。") 