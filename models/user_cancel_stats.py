from extension import db

class UserCancelStats(db.Model):
    __tablename__ = 'user_cancel_stats'
    user_id = db.Column(db.Integer, primary_key=True)
    cancelled_orders = db.Column(db.Integer, default=0)