from extension import db

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    region = db.Column(db.String(50))
    publisher = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date)
    purchase_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)