#!/usr/bin/env python3
"""
创建示例素材图片用于测试
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_material(category, name, filename, color):
    """创建示例素材图片"""
    # 创建目录
    base_path = "static/ideal_character"
    category_path = os.path.join(base_path, category)
    os.makedirs(category_path, exist_ok=True)
    
    # 创建图片 - 正方形尺寸
    width, height = 400, 400
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制背景框
    draw.rectangle([50, 50, width-50, height-50], fill=(255, 255, 255, 100), outline=color, width=3)
    
    # 绘制特征标识
    draw.rectangle([100, 100, width-100, height-100], fill=color, outline=(255, 255, 255, 255), width=2)
    
    # 添加文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # 使用默认字体
        font = ImageFont.load_default()
    
    # 绘制类别和名称
    text = f"{category}\n{name}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文字背景
    draw.rectangle([x-10, y-10, x+text_width+10, y+text_height+10], 
                   fill=(255, 255, 255, 200))
    
    # 绘制文字
    draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
    
    # 保存图片
    file_path = os.path.join(category_path, filename)
    img.save(file_path, 'PNG')
    print(f"✅ 创建: {file_path}")

def create_all_sample_materials():
    """创建所有示例素材"""
    print("🎨 创建示例素材图片...")
    
    # 定义素材配置
    materials = {
        'hair': {
            '红': ('red.png', (255, 0, 0, 255)),
            '蓝': ('blue.png', (0, 0, 255, 255)),
            '黄': ('yellow.png', (255, 255, 0, 255)),
            '棕': ('brown.png', (139, 69, 19, 255)),
            '紫': ('purple.png', (128, 0, 128, 255)),
            '白': ('white.png', (255, 255, 255, 255)),
            '黑': ('black.png', (0, 0, 0, 255)),
            '绿': ('green.png', (0, 128, 0, 255))
        },
        'eyes': {
            '红': ('red.png', (255, 0, 0, 255)),
            '蓝': ('blue.png', (0, 0, 255, 255)),
            '黄': ('yellow.png', (255, 255, 0, 255)),
            '棕': ('brown.png', (139, 69, 19, 255)),
            '紫': ('purple.png', (128, 0, 128, 255)),
            '黑': ('black.png', (0, 0, 0, 255)),
            '绿': ('green.png', (0, 128, 0, 255))
        },
        'glasses': {
            '戴眼镜': ('with.png', (0, 100, 0, 255)),
            '无眼镜': ('without.png', (128, 128, 128, 255))
        },
        'aura': {
            '阳光': ('sunny.png', (255, 165, 0, 255)),
            '温柔': ('gentle.png', (255, 182, 193, 255)),
            '高冷': ('cold.png', (70, 130, 180, 255)),
            '傲娇': ('tsundere.png', (255, 20, 147, 255)),
            '病娇': ('yandere.png', (220, 20, 60, 255))
        },
        'age': {
            '正太': ('shota.png', (255, 215, 0, 255)),
            '成男': ('adult.png', (0, 0, 139, 255)),
            '大叔': ('uncle.png', (105, 105, 105, 255))
        }
    }
    
    # 创建所有素材
    for category, items in materials.items():
        print(f"\n📁 创建 {category} 类别素材:")
        for name, (filename, color) in items.items():
            create_sample_material(category, name, filename, color)
    
    print(f"\n✅ 所有示例素材创建完成！")
    print(f"素材位置: static/ideal_character/")
    print(f"现在可以运行测试脚本验证功能了！")

if __name__ == "__main__":
    create_all_sample_materials() 