from extension import db

class GameUser(db.Model):
    __tablename__ = 'game_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    status = db.Column(db.String(10))  # 'wish', 'playing', 'played'
    rating = db.Column(db.Float)  # 1~5分，支持半星
    __table_args__ = (db.UniqueConstraint('user_id', 'game_id', name='_user_game_uc'),) 