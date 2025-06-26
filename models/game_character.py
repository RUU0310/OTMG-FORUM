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

class GameCharacterRating(db.Model):
    __tablename__ = 'game_character_rating'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('game_character.id'), nullable=False)
    appearance_score = db.Column(db.Float, nullable=True)  # 外貌分，0-10，支持半星
    personality_score = db.Column(db.Float, nullable=True) # 性格分，0-10，支持半星
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    # 允许部分角色无评分，用户可只评一个维度或都不评
