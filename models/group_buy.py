from extension import db
from datetime import datetime

class GroupBuyProduct(db.Model):
    """拼团商品表"""
    __tablename__ = 'group_buy_product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 商品名称
    description = db.Column(db.Text)  # 商品描述
    image = db.Column(db.String(255))  # 商品图片

class GroupBuyCharacter(db.Model):
    """拼团角色表"""
    __tablename__ = 'group_buy_character'
    character_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('group_buy_product.product_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 角色名称
    image = db.Column(db.String(255))  # 角色图片
    is_popular = db.Column(db.Boolean, default=False)  # 是否热门角色

class GroupBuy(db.Model):
    """拼团表"""
    __tablename__ = 'group_buy'
    group_buy_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('group_buy_product.product_id'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 团长ID
    title = db.Column(db.String(200), nullable=False)  # 拼团标题
    description = db.Column(db.Text)  # 拼团描述
    contact_info = db.Column(db.Text)  # 联系方式
    average_price = db.Column(db.Numeric(10, 2), nullable=False)  # 均价
    status = db.Column(db.String(20), default='recruiting')  # 状态：recruiting, full, completed, cancelled
    deadline = db.Column(db.DateTime)  # 拼团截止时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GroupBuyCharacterAdjustment(db.Model):
    __tablename__ = 'group_buy_character_adjustment'
    id = db.Column(db.Integer, primary_key=True)
    group_buy_id = db.Column(db.Integer, db.ForeignKey('group_buy.group_buy_id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('group_buy_character.character_id'), nullable=False)
    price_adjustment = db.Column(db.Numeric(10, 2), default=0.00)
    max_count = db.Column(db.Integer, default=1)  # 新增字段：可拼团个数

class GroupBuyMember(db.Model):
    """拼团成员表"""
    __tablename__ = 'group_buy_member'
    id = db.Column(db.Integer, primary_key=True)
    group_buy_id = db.Column(db.Integer, db.ForeignKey('group_buy.group_buy_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('group_buy_character.character_id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 状态：pending, approved, rejected, cancelled
    final_price = db.Column(db.Numeric(10, 2))  # 最终价格（均价+调整价）
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)  # 团长批准时间

class UserGroupBuyStats(db.Model):
    """用户拼团统计表"""
    __tablename__ = 'user_group_buy_stats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    successful_groups = db.Column(db.Integer, default=0)  # 成功开团数
    cancelled_orders = db.Column(db.Integer, default=0)  # 跑单数
    total_participated = db.Column(db.Integer, default=0)  # 总参与拼团数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GroupBuyRequest(db.Model):
    __tablename__ = 'group_buy_request'
    id = db.Column(db.Integer, primary_key=True)
    group_buy_id = db.Column(db.Integer, db.ForeignKey('group_buy.group_buy_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('group_buy_character.character_id'), nullable=False)
    count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # 团长
    message = db.Column(db.Text)  # 申请留言/备注 