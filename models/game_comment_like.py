from extension import db

class GameCommentLike(db.Model):
    __tablename__ = 'game_comment_like'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('game_comment.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='_user_comment_uc'),) 