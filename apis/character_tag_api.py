from flask import Blueprint, request, jsonify
from extension import db
from models.character_tag import Tag, CharacterTag
from models.game_character import GameCharacter
from datetime import datetime

character_tag_api = Blueprint('character_tag_api', __name__)

# 标签管理
@character_tag_api.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    results = [tag_to_dict(t) for t in tags]
    return jsonify({'status': 'success', 'results': results})

def tag_to_dict(tag):
    return {
        'id': tag.id,
        'name': tag.name,
        'type': tag.type,
        'category': tag.category,
        'options': tag.options,
        'is_multiple': tag.is_multiple,
        'description': tag.description,
        'is_active': tag.is_active,
        'created_at': tag.created_at,
        'updated_at': tag.updated_at
    }

@character_tag_api.route('/tags', methods=['POST'])
def add_tag():
    data = request.json
    tag = Tag(
        name=data.get('name'),
        type=data.get('type'),
        category=data.get('category'),
        options=data.get('options', ''),
        is_multiple=data.get('is_multiple', False),
        description=data.get('description', ''),
        is_active=data.get('is_active', True),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(tag)
    db.session.commit()
    return jsonify({'status': 'success', 'id': tag.id})

@character_tag_api.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'status': 'error', 'message': '标签不存在'}), 404
    data = request.json
    for field in ['name', 'type', 'category', 'options', 'is_multiple', 'description', 'is_active']:
        if field in data:
            setattr(tag, field, data[field])
    tag.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'status': 'success'})

@character_tag_api.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'status': 'error', 'message': '标签不存在'}), 404
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'status': 'success'})

# 角色标签管理
@character_tag_api.route('/character-tags', methods=['GET'])
def get_character_tags():
    character_id = request.args.get('character_id')
    q = CharacterTag.query
    if character_id:
        q = q.filter_by(character_id=character_id)
    results = [character_tag_to_dict(t) for t in q.all()]
    return jsonify({'status': 'success', 'results': results})

def character_tag_to_dict(ct):
    return {
        'id': ct.id,
        'character_id': ct.character_id,
        'tag_id': ct.tag_id,
        'value': ct.value,
        'tag': tag_to_dict(ct.tag) if ct.tag else None,
        'created_at': ct.created_at,
        'updated_at': ct.updated_at
    }

@character_tag_api.route('/character-tags', methods=['POST'])
def add_character_tag():
    data = request.json
    ct = CharacterTag(
        character_id=data.get('character_id'),
        tag_id=data.get('tag_id'),
        value=data.get('value'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(ct)
    db.session.commit()
    return jsonify({'status': 'success', 'id': ct.id})

@character_tag_api.route('/character-tags/<int:ct_id>', methods=['PUT'])
def update_character_tag(ct_id):
    ct = CharacterTag.query.get(ct_id)
    if not ct:
        return jsonify({'status': 'error', 'message': '角色标签不存在'}), 404
    data = request.json
    if 'value' in data:
        ct.value = data['value']
    ct.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'status': 'success'})

@character_tag_api.route('/character-tags/<int:ct_id>', methods=['DELETE'])
def delete_character_tag(ct_id):
    ct = CharacterTag.query.get(ct_id)
    if not ct:
        return jsonify({'status': 'error', 'message': '角色标签不存在'}), 404
    db.session.delete(ct)
    db.session.commit()
    return jsonify({'status': 'success'})

@character_tag_api.route('/character-tags/batch', methods=['POST'])
def batch_add_character_tags():
    data = request.json
    records = data.get('records', [])
    created_ids = []
    for rec in records:
        ct = CharacterTag(
            character_id=rec.get('character_id'),
            tag_id=rec.get('tag_id'),
            value=rec.get('value'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(ct)
        db.session.flush()  # 获取id
        created_ids.append(ct.id)
    db.session.commit()
    return jsonify({'status': 'success', 'ids': created_ids}) 