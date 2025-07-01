from flask import Flask
from flask_cors import CORS
from extension import db
from apis.game_api import game_bp
from apis.user_api import user_bp, login as user_login
from apis.upload_api import upload_bp
from apis.group_api import group_api
from apis.group_buy_api import group_buy_api
from apis import message_api
from apis.game_character_api import game_character_api
from apis.character_tag_api import character_tag_api
from apis.fantasy_chat_api import fantasy_chat_api
from apis.ideal_character_api import ideal_character_api
import logging
import os
from models.game_user import GameUser
from models.game_comment import GameComment
from models.game_comment_like import GameCommentLike
from models.game_character import GameCharacter
from models.group_post import Group, Post, PostCategory, PostLike, PollOption, PollVote
from models.group_buy import GroupBuyProduct, GroupBuyCharacter, GroupBuy, GroupBuyMember, UserGroupBuyStats
from models.user_cancel_stats import UserCancelStats
from models.character_tag import Tag, CharacterTag

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-please-change'  # 用于session，生产环境请更换
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 设置最大文件上传大小为5MB
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "games.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(game_bp)
app.register_blueprint(user_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(group_api)
app.register_blueprint(group_buy_api, url_prefix='/api/group-buy')
app.register_blueprint(message_api.bp)
app.register_blueprint(game_character_api)
app.register_blueprint(character_tag_api, url_prefix='/api')
app.register_blueprint(fantasy_chat_api, url_prefix='/api')
app.register_blueprint(ideal_character_api, url_prefix='/api')
app.add_url_rule('/users/login', view_func=user_login, methods=['POST'])

@app.cli.command()
def create():
    db.create_all()
    logging.info(f"数据库已创建: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    app.run() 