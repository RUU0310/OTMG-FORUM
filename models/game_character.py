from extension import db
from sqlalchemy.dialects.sqlite import JSON

class GameCharacter(db.Model):
    __tablename__ = 'game_character'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)      # 姓名
    cv = db.Column(db.String(100), nullable=False)        # 声优
    avatar = db.Column(db.String(255))
    description = db.Column(db.Text)
    extra_info = db.Column(JSON)  # 其它官方设定
    role_type = db.Column(db.String(20), nullable=False, default='可攻略')  # 角色类型：女主/可攻略/不可攻略
