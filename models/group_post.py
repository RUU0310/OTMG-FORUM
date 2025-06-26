from extension import db
from datetime import datetime

class Group(db.Model):
    __tablename__ = 'groups'
    group_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    avatar = db.Column(db.String(255))

class PostCategory(db.Model):
    __tablename__ = 'post_category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(100))

class Post(db.Model):
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200),nullable=False)
    content = db.Column(db.Text)
    images = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('post_category.category_id'), nullable=True)
    is_poll = db.Column(db.Boolean, default=False)
    poll_type = db.Column(db.String(10), default='single')  # 'single' or 'multi'
    poll_deadline = db.Column(db.DateTime, nullable=True)

class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PollOption(db.Model):
    __tablename__ = 'poll_option'
    option_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    vote_count = db.Column(db.Integer, default=0)

class PollVote(db.Model):
    __tablename__ = 'poll_vote'
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('poll_option.option_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupMember(db.Model):
    __tablename__ = 'group_member'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow) 

class PostComment(db.Model):
    __tablename__ = 'post_comment'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'), nullable=True)  # 支持回复
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PostCommentLike(db.Model):
    __tablename__ = 'post_comment_like'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PostFavorite(db.Model):
    __tablename__ = 'post_favorite'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 