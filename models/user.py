from extension import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    role = db.Column(db.String(20), nullable=False)
