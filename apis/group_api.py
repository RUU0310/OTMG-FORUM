from flask import Blueprint, request, jsonify
from models.group_post import Group, PostCategory, Post, PostLike, PollOption, PollVote, GroupMember, PostComment, PostCommentLike, PostFavorite
from models.user import User
from extension import db
from datetime import datetime, timedelta
import json

group_api = Blueprint('group_api', __name__)

# ----------------- Group -----------------
@group_api.route('/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    result = []
    for g in groups:
        member_count = GroupMember.query.filter_by(group_id=g.group_id).count()
        result.append({'group_id': g.group_id, 'game_id': g.game_id, 'name': g.name, 'description': g.description, 'avatar': g.avatar, 'member_count': member_count})
    return jsonify(result)

@group_api.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    g = Group.query.get_or_404(group_id)
    member_count = GroupMember.query.filter_by(group_id=g.group_id).count()
    return jsonify({'group_id': g.group_id, 'game_id': g.game_id, 'name': g.name, 'description': g.description, 'avatar': g.avatar, 'member_count': member_count})

@group_api.route('/groups', methods=['POST'])
def create_group():
    data = request.json
    group = Group(game_id=data.get('game_id'), name=data['name'], description=data.get('description'), avatar=data.get('avatar'))
    db.session.add(group)
    db.session.commit()
    return jsonify({'status': 'success', 'group_id': group.group_id})

@group_api.route('/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.json
    group.name = data.get('name', group.name)
    group.description = data.get('description', group.description)
    group.avatar = data.get('avatar', group.avatar)
    group.game_id = data.get('game_id', group.game_id)
    db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'status': 'success'})

# ----------------- PostCategory -----------------
@group_api.route('/post-categories', methods=['GET'])
def get_post_categories():
    cats = PostCategory.query.all()
    return jsonify([{'category_id': c.category_id, 'name': c.name, 'description': c.description} for c in cats])

@group_api.route('/post-categories', methods=['POST'])
def create_post_category():
    data = request.json
    cat = PostCategory(name=data['name'], description=data.get('description'))
    db.session.add(cat)
    db.session.commit()
    return jsonify({'status': 'success', 'category_id': cat.category_id})

@group_api.route('/post-categories/<int:category_id>', methods=['PUT'])
def update_post_category(category_id):
    cat = PostCategory.query.get_or_404(category_id)
    data = request.json
    cat.name = data.get('name', cat.name)
    cat.description = data.get('description', cat.description)
    db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/post-categories/<int:category_id>', methods=['DELETE'])
def delete_post_category(category_id):
    cat = PostCategory.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'status': 'success'})

# ----------------- Post -----------------
@group_api.route('/groups/<int:group_id>/posts', methods=['GET'])
def get_posts(group_id):
    posts = Post.query.filter_by(group_id=group_id).order_by(Post.created_at.desc()).all()
    result = []
    for p in posts:
        if not p or not p.post_id:
            continue
        # 获取分类信息
        category_name = None
        if p.category_id:
            category = PostCategory.query.get(p.category_id)
            category_name = category.name if category else None
        # 获取点赞数
        like_count = PostLike.query.filter_by(post_id=p.post_id).count()
        # 获取用户信息
        user = User.query.get(p.user_id)
        username = user.username if user else None
        nickname = user.nickname if user else None
        post_data = {
            'post_id': p.post_id, 
            'user_id': p.user_id, 
            'username': username,
            'nickname': nickname,
            'title': p.title, 
            'content': p.content, 
            'images': p.images, 
            'created_at': p.created_at, 
            'updated_at': p.updated_at, 
            'category_id': p.category_id,
            'category_name': category_name,
            'is_poll': p.is_poll, 
            'poll_type': p.poll_type, 
            'poll_deadline': p.poll_deadline,
            'like_count': like_count
        }
        # 如果是投票，获取投票选项
        if p.is_poll:
            poll_options = PollOption.query.filter_by(post_id=p.post_id).all()
            post_data['poll_options'] = [
                {
                    'option_id': opt.option_id,
                    'text': opt.text,
                    'vote_count': opt.vote_count
                } for opt in poll_options if opt and opt.option_id
            ]
        result.append(post_data)
    return jsonify(result)

@group_api.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    p = Post.query.get_or_404(post_id)
    user_id = request.args.get('user_id', type=int)
    # 获取分类信息
    category_name = None
    if p.category_id:
        category = PostCategory.query.get(p.category_id)
        category_name = category.name if category else None
    # 获取点赞数
    like_count = PostLike.query.filter_by(post_id=p.post_id).count()
    # 获取当前用户是否已点赞
    liked = False
    if user_id:
        liked = PostLike.query.filter_by(post_id=p.post_id, user_id=user_id).first() is not None
    # 获取用户信息
    user = User.query.get(p.user_id)
    username = user.username if user else None
    nickname = user.nickname if user else None
    avatar = user.avatar if user else None
    post_data = {
        'post_id': p.post_id, 
        'group_id': p.group_id, 
        'user_id': p.user_id, 
        'username': username,
        'nickname': nickname,
        'avatar': avatar,
        'title': p.title, 
        'content': p.content, 
        'images': p.images, 
        'created_at': p.created_at, 
        'updated_at': p.updated_at, 
        'category_id': p.category_id,
        'category_name': category_name,
        'is_poll': p.is_poll, 
        'poll_type': p.poll_type, 
        'poll_deadline': p.poll_deadline,
        'like_count': like_count,
        'liked': liked
    }
    # 如果是投票，获取投票选项
    if p.is_poll:
        poll_options = PollOption.query.filter_by(post_id=p.post_id).all()
        post_data['poll_options'] = [
            {
                'option_id': opt.option_id,
                'text': opt.text,
                'vote_count': opt.vote_count
            } for opt in poll_options
        ]
    return jsonify(post_data)

@group_api.route('/groups/<int:group_id>/posts', methods=['POST'])
def create_post(group_id):
    data = request.json
    user_id = data['user_id']
    
    # 校验是否为小组成员
    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({'status': 'error', 'message': '请先加入该小组才能发帖'}), 403
    
    # 校验必填字段
    if not data.get('title'):
        return jsonify({'status': 'error', 'message': '请填写标题'}), 400
    
    # 处理投票截止时间
    poll_deadline = None
    if data.get('poll_deadline'):
        try:
            poll_deadline = datetime.fromisoformat(data['poll_deadline'].replace('Z', '+00:00'))
        except:
            pass
    
    post = Post(
        group_id=group_id, 
        user_id=user_id, 
        title=data['title'], 
        content=data.get('content', ''), 
        images=data.get('images'), 
        category_id=data.get('category_id'), 
        is_poll=data.get('is_poll', False), 
        poll_type=data.get('poll_type', 'single'), 
        poll_deadline=poll_deadline
    )
    db.session.add(post)
    db.session.flush()  # 获取post_id
    
    # 如果是投票帖，创建投票选项
    if data.get('is_poll') and data.get('poll_options'):
        for option_text in data['poll_options']:
            if option_text.strip():  # 只添加非空选项
                option = PollOption(post_id=post.post_id, text=option_text.strip())
                db.session.add(option)
    
    db.session.commit()
    return jsonify({'status': 'success', 'post_id': post.post_id})

@group_api.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.json
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.images = data.get('images', post.images)
    post.category_id = data.get('category_id', post.category_id)
    post.is_poll = data.get('is_poll', post.is_poll)
    post.poll_type = data.get('poll_type', post.poll_type)
    
    # 处理投票截止时间
    if data.get('poll_deadline'):
        try:
            post.poll_deadline = datetime.fromisoformat(data['poll_deadline'].replace('Z', '+00:00'))
        except:
            pass
    
    db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'status': 'success'})

# ----------------- PostLike -----------------
@group_api.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    data = request.json
    user_id = data['user_id']
    if not PostLike.query.filter_by(post_id=post_id, user_id=user_id).first():
        like = PostLike(post_id=post_id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/posts/<int:post_id>/like', methods=['DELETE'])
def unlike_post(post_id):
    user_id = request.args.get('user_id', type=int)
    like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/posts/<int:post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    count = PostLike.query.filter_by(post_id=post_id).count()
    return jsonify({'post_id': post_id, 'like_count': count})

# ----------------- PollOption -----------------
@group_api.route('/posts/<int:post_id>/poll-options', methods=['GET'])
def get_poll_options(post_id):
    opts = PollOption.query.filter_by(post_id=post_id).all()
    return jsonify([{'option_id': o.option_id, 'text': o.text, 'vote_count': o.vote_count} for o in opts])

@group_api.route('/posts/<int:post_id>/poll-options', methods=['POST'])
def create_poll_option(post_id):
    data = request.json
    opt = PollOption(post_id=post_id, text=data['text'])
    db.session.add(opt)
    db.session.commit()
    return jsonify({'status': 'success', 'option_id': opt.option_id})

@group_api.route('/poll-options/<int:option_id>', methods=['PUT'])
def update_poll_option(option_id):
    opt = PollOption.query.get_or_404(option_id)
    data = request.json
    opt.text = data.get('text', opt.text)
    db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/poll-options/<int:option_id>', methods=['DELETE'])
def delete_poll_option(option_id):
    opt = PollOption.query.get_or_404(option_id)
    db.session.delete(opt)
    db.session.commit()
    return jsonify({'status': 'success'})

# ----------------- PollVote -----------------
@group_api.route('/poll-options/<int:option_id>/vote', methods=['POST'])
def vote_poll_option(option_id):
    data = request.json
    user_id = data['user_id']
    
    # 检查是否已经投过票
    existing_vote = PollVote.query.filter_by(option_id=option_id, user_id=user_id).first()
    if existing_vote:
        return jsonify({'status': 'error', 'message': '您已经投过票了'}), 400
    
    # 获取投票选项和帖子信息
    option = PollOption.query.get_or_404(option_id)
    post = Post.query.get_or_404(option.post_id)
    
    # 如果是单选投票，检查用户是否已经对该帖子的其他选项投过票
    if post.poll_type == 'single':
        # 获取该帖子的所有选项ID
        all_option_ids = [opt.option_id for opt in PollOption.query.filter_by(post_id=post.post_id).all()]
        # 检查用户是否已经对任何选项投过票
        existing_votes = PollVote.query.filter(
            PollVote.option_id.in_(all_option_ids),
            PollVote.user_id == user_id
        ).all()
        if existing_votes:
            return jsonify({'status': 'error', 'message': '单选投票中您已经投过票了'}), 400
    
    # 创建投票记录
    vote = PollVote(option_id=option_id, user_id=user_id)
    db.session.add(vote)
    
    # 增加投票计数
    option.vote_count = (option.vote_count or 0) + 1
    db.session.commit()
    
    return jsonify({'status': 'success'})

@group_api.route('/poll-options/<int:option_id>/vote', methods=['DELETE'])
def unvote_poll_option(option_id):
    user_id = request.args.get('user_id', type=int)
    vote = PollVote.query.filter_by(option_id=option_id, user_id=user_id).first()
    if vote:
        db.session.delete(vote)
        # 减少投票计数
        opt = PollOption.query.get(option_id)
        if opt and opt.vote_count:
            opt.vote_count -= 1
        db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/poll-options/<int:option_id>/votes', methods=['GET'])
def get_poll_option_votes(option_id):
    count = PollVote.query.filter_by(option_id=option_id).count()
    return jsonify({'option_id': option_id, 'vote_count': count})

# 检查用户是否已投票
@group_api.route('/posts/<int:post_id>/user-votes/<int:user_id>', methods=['GET'])
def get_user_votes_for_post(post_id, user_id):
    # 获取该帖子的所有选项ID
    option_ids = [opt.option_id for opt in PollOption.query.filter_by(post_id=post_id).all()]
    # 获取用户对这些选项的投票
    votes = PollVote.query.filter(
        PollVote.option_id.in_(option_ids),
        PollVote.user_id == user_id
    ).all()
    voted_option_ids = [vote.option_id for vote in votes]
    return jsonify({'voted_option_ids': voted_option_ids})

@group_api.route('/groups/<int:group_id>/members', methods=['GET'])
def get_group_members(group_id):
    members = GroupMember.query.filter_by(group_id=group_id).all()
    return jsonify([{'user_id': m.user_id, 'joined_at': m.joined_at} for m in members])

@group_api.route('/groups/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        gm = GroupMember(group_id=group_id, user_id=user_id)
        db.session.add(gm)
        db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/groups/<int:group_id>/leave', methods=['POST'])
def leave_group(group_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    gm = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if gm:
        db.session.delete(gm)
        db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/users/<int:user_id>/groups', methods=['GET'])
def get_user_groups(user_id):
    group_ids = [gm.group_id for gm in GroupMember.query.filter_by(user_id=user_id).all()]
    groups = Group.query.filter(Group.group_id.in_(group_ids)).all()
    result = []
    for g in groups:
        member_count = GroupMember.query.filter_by(group_id=g.group_id).count()
        result.append({'group_id': g.group_id, 'game_id': g.game_id, 'name': g.name, 'description': g.description, 'avatar': g.avatar, 'member_count': member_count})
    return jsonify(result)

# 获取评论（楼中楼结构）
@group_api.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    user_id = request.args.get('user_id', type=int)
    comments = PostComment.query.filter_by(post_id=post_id).order_by(PostComment.created_at.asc()).all()
    user_map = {u.user_id: u for u in User.query.filter(User.user_id.in_([c.user_id for c in comments])).all()}
    comment_dict = {}
    for c in comments:
        liked = False
        if user_id:
            liked = PostCommentLike.query.filter_by(comment_id=c.id, user_id=user_id).first() is not None
        comment_dict[c.id] = {
            'id': c.id,
            'user_id': c.user_id,
            'nickname': user_map.get(c.user_id).nickname if user_map.get(c.user_id) else '',
            'avatar': user_map.get(c.user_id).avatar if user_map.get(c.user_id) else '',
            'content': c.content,
            'parent_id': c.parent_id,
            'created_at': c.created_at,
            'like_count': PostCommentLike.query.filter_by(comment_id=c.id).count(),
            'liked': liked,
            'children': []
        }
    root_comments = []
    for c in comment_dict.values():
        if c['parent_id']:
            parent = comment_dict.get(c['parent_id'])
            if parent:
                parent['children'].append(c)
            else:
                c['content'] = '[该评论已被删除]'
                root_comments.append(c)
        else:
            root_comments.append(c)
    return jsonify(root_comments)

# 新增评论/回复
@group_api.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_post_comment(post_id):
    data = request.json
    user_id = data['user_id']
    content = data['content']
    parent_id = data.get('parent_id')
    comment = PostComment(post_id=post_id, user_id=user_id, content=content, parent_id=parent_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'status': 'success', 'comment_id': comment.id})

# 点赞评论
@group_api.route('/comments/<int:comment_id>/like', methods=['POST'])
def like_post_comment(comment_id):
    user_id = request.json['user_id']
    if not PostCommentLike.query.filter_by(comment_id=comment_id, user_id=user_id).first():
        like = PostCommentLike(comment_id=comment_id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
    return jsonify({'status': 'success'})

# 取消点赞
@group_api.route('/comments/<int:comment_id>/like', methods=['DELETE'])
def unlike_post_comment(comment_id):
    user_id = request.args.get('user_id', type=int)
    like = PostCommentLike.query.filter_by(comment_id=comment_id, user_id=user_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return jsonify({'status': 'success'})

# 收藏帖子
@group_api.route('/posts/<int:post_id>/favorite', methods=['POST'])
def favorite_post(post_id):
    user_id = request.json['user_id']
    if not PostFavorite.query.filter_by(post_id=post_id, user_id=user_id).first():
        fav = PostFavorite(post_id=post_id, user_id=user_id)
        db.session.add(fav)
        db.session.commit()
    return jsonify({'status': 'success'})

# 取消收藏
@group_api.route('/posts/<int:post_id>/favorite', methods=['DELETE'])
def unfavorite_post(post_id):
    user_id = request.args.get('user_id', type=int)
    fav = PostFavorite.query.filter_by(post_id=post_id, user_id=user_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return jsonify({'status': 'success'})

# 获取收藏状态
@group_api.route('/posts/<int:post_id>/favorite', methods=['GET'])
def get_favorite_status(post_id):
    user_id = request.args.get('user_id', type=int)
    is_fav = PostFavorite.query.filter_by(post_id=post_id, user_id=user_id).first() is not None
    return jsonify({'is_favorite': is_fav})

# 伪删除评论（内容改为"该评论已被删除"）
@group_api.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['PUT'])
def update_or_delete_comment(post_id, comment_id):
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content')
    comment = PostComment.query.filter_by(id=comment_id, post_id=post_id, user_id=user_id).first()
    if not comment:
        return jsonify({'status': 'error', 'message': '评论不存在或无权限'}), 403
    if content == '[该评论已被删除]':
        comment.content = '[该评论已被删除]'
    else:
        if not content or not content.strip():
            return jsonify({'status': 'error', 'message': '内容不能为空'}), 400
        comment.content = content.strip()
    db.session.commit()
    return jsonify({'status': 'success'})

@group_api.route('/groups/hot-posts', methods=['POST'])
def get_hot_posts():
    data = request.json
    group_ids = data.get('group_ids', [])
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    # 查找一周内这些小组的帖子
    posts = Post.query.filter(
        Post.group_id.in_(group_ids),
        Post.created_at >= week_ago
    ).all()
    post_stats = []
    for p in posts:
        like_count = PostLike.query.filter_by(post_id=p.post_id).filter(PostLike.created_at >= week_ago).count()
        comment_count = PostComment.query.filter_by(post_id=p.post_id).filter(PostComment.created_at >= week_ago).count()
        post_stats.append((p, like_count, comment_count))
    # 按点赞+评论数排序，取前10
    post_stats.sort(key=lambda x: (x[1] + x[2]), reverse=True)
    top_posts = [x[0] for x in post_stats[:10]]
    result = []
    for p in top_posts:
        category_name = None
        if p.category_id:
            category = PostCategory.query.get(p.category_id)
            category_name = category.name if category else None
        like_count = PostLike.query.filter_by(post_id=p.post_id).count()
        user = User.query.get(p.user_id)
        username = user.username if user else None
        nickname = user.nickname if user else None
        post_data = {
            'post_id': p.post_id,
            'user_id': p.user_id,
            'username': username,
            'nickname': nickname,
            'title': p.title,
            'content': p.content,
            'images': p.images,
            'created_at': p.created_at,
            'updated_at': p.updated_at,
            'category_id': p.category_id,
            'category_name': category_name,
            'is_poll': p.is_poll,
            'poll_type': p.poll_type,
            'poll_deadline': p.poll_deadline,
            'like_count': like_count
        }
        result.append(post_data)
    return jsonify(result)