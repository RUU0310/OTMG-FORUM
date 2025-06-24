from flask import Flask
from flask_cors import CORS
from extension import db
from apis.game_api import game_bp
from apis.user_api import user_bp, login as user_login
from apis.upload_api import upload_bp
import logging
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-please-change'  # 用于session，生产环境请更换
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "games.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(game_bp)
app.register_blueprint(user_bp)
app.register_blueprint(upload_bp)
app.add_url_rule('/users/login', view_func=user_login, methods=['POST'])

@app.cli.command()
def create():
    db.create_all()
    logging.info(f"数据库已创建: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    app.run() 