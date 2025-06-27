from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from extension import db

class Tag(db.Model):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True, comment='标签名')
    type = Column(String(32), nullable=False, comment='标签类型，如 appearance/personality')
    category = Column(String(32), nullable=False, comment='标签分类，如外貌/性格')
    options = Column(Text, nullable=True, comment='可选项，逗号分隔')
    is_multiple = Column(Boolean, default=False, comment='是否多选')
    description = Column(String(255), default='', comment='标签描述')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CharacterTag(db.Model):
    __tablename__ = 'character_tags'
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)
    value = Column(String(64), nullable=False, comment='标签值')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tag = relationship('Tag') 