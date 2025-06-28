from flask import Blueprint, request, jsonify, send_file
from PIL import Image
import os
import io
import base64
from models.character_tag import Tag

ideal_character_api = Blueprint('ideal_character_api', __name__)

# 素材映射表
MATERIAL_MAPPING = {
    'hair': {
        '红': 'red.png',
        '蓝': 'blue.png', 
        '黄': 'yellow.png',
        '棕': 'brown.png',
        '紫': 'purple.png',
        '白': 'white.png',
        '黑': 'black.png',
        '绿': 'green.png'
    },
    'eyes': {
        '红': 'red.png',
        '蓝': 'blue.png',
        '黄': 'yellow.png', 
        '棕': 'brown.png',
        '紫': 'purple.png',
        '黑': 'black.png',
        '绿': 'green.png'
    },
    'glasses': {
        '眼镜': 'with.png',
        '无眼镜': 'without.png'
    },
    'aura': {
        '阳光': 'sunny.png',
        '温柔': 'gentle.png',
        '高冷': 'cold.png',
        '傲娇': 'tsundere.png',
        '病娇': 'yandere.png'
    },
    'age': {
        '正太': 'shota.png',
        '成男': 'adult.png',
        '大叔': 'uncle.png'
    }
}

def get_material_path(category, value):
    """获取素材文件路径"""
    if category not in MATERIAL_MAPPING or value not in MATERIAL_MAPPING[category]:
        return None
    
    filename = MATERIAL_MAPPING[category][value]
    base_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'ideal_character')
    file_path = os.path.join(base_path, category, filename)
    
    return file_path if os.path.exists(file_path) else None

def composite_character_image(traits):
    """合成角色图片"""
    try:
        # 创建基础画布（透明背景）- 正方形尺寸
        canvas_width, canvas_height = 400, 400
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        
        # 按顺序合成图层（从底层到顶层）
        layer_order = ['hair','eyes','age', 'aura', 'glasses']
        
        for layer in layer_order:
            if layer in traits and traits[layer]:
                material_path = get_material_path(layer, traits[layer])
                if material_path:
                    try:
                        layer_img = Image.open(material_path).convert('RGBA')
                        # 调整图层大小以匹配画布（正方形）
                        layer_img = layer_img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                        # 合成图层
                        canvas = Image.alpha_composite(canvas, layer_img)
                    except Exception as e:
                        print(f"加载图层失败 {layer}: {e}")
                        continue
        
        return canvas
        
    except Exception as e:
        print(f"合成图片失败: {e}")
        return None

@ideal_character_api.route('/generate-ideal-character', methods=['POST'])
def generate_ideal_character():
    """生成理想形象图片"""
    try:
        data = request.json
        traits = data.get('traits', {})
        
        # 合成图片
        composite_img = composite_character_image(traits)
        
        if composite_img is None:
            return jsonify({
                'success': False,
                'message': '图片合成失败'
            })
        
        # 将图片转换为base64
        img_buffer = io.BytesIO()
        composite_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # 转换为base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{img_base64}'
        })
        
    except Exception as e:
        print(f"生成理想形象失败: {e}")
        return jsonify({
            'success': False,
            'message': '生成失败'
        })

@ideal_character_api.route('/ideal-character-materials', methods=['GET'])
def get_materials():
    """获取可用的素材列表"""
    try:
        materials = {}
        base_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'ideal_character')
        
        for category in MATERIAL_MAPPING.keys():
            category_path = os.path.join(base_path, category)
            if os.path.exists(category_path):
                materials[category] = list(MATERIAL_MAPPING[category].keys())
            else:
                materials[category] = []
        
        return jsonify({
            'success': True,
            'materials': materials
        })
        
    except Exception as e:
        print(f"获取素材列表失败: {e}")
        return jsonify({
            'success': False,
            'message': '获取素材列表失败'
        })

@ideal_character_api.route('/tag-categories', methods=['GET'])
def get_tag_categories():
    """获取标签分类信息"""
    try:
        # 从数据库获取所有标签
        tags = Tag.query.filter_by(is_active=True).all()
        
        print(f"🔍 找到 {len(tags)} 个活跃标签")
        
        # 按type分类
        appearance_tags = []
        personality_tags = []
        other_tags = []
        
        for tag in tags:
            print(f"标签: {tag.name}, type: {tag.type}, category: {tag.category}")
            if tag.type == 'appearance':
                appearance_tags.append(tag.name)
            elif tag.type == 'personality':
                personality_tags.append(tag.name)
            else:
                other_tags.append(tag.name)
        
        print(f"外貌标签: {appearance_tags}")
        print(f"性格标签: {personality_tags}")
        print(f"其他标签: {other_tags}")
        
        return jsonify({
            'success': True,
            'appearance_tags': appearance_tags,
            'personality_tags': personality_tags,
            'other_tags': other_tags,
            'total_tags': len(tags),
            'all_tags': [
                {
                    'name': tag.name,
                    'type': tag.type,
                    'category': tag.category
                } for tag in tags
            ]
        })
        
    except Exception as e:
        print(f"获取标签分类失败: {e}")
        return jsonify({
            'success': False,
            'message': '获取标签分类失败'
        }) 