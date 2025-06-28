#!/usr/bin/env python3
"""
检查数据库中的标签分类
"""

from app import app
from models.character_tag import Tag

def check_tags():
    """检查标签分类"""
    with app.app_context():
        print("🏷️ 检查数据库中的标签分类")
        print("=" * 50)
        
        # 获取所有标签
        tags = Tag.query.filter_by(is_active=True).all()
        
        print(f"总共有 {len(tags)} 个活跃标签")
        print()
        
        # 按type分类
        appearance_tags = []
        personality_tags = []
        other_tags = []
        
        for tag in tags:
            if tag.type == 'appearance':
                appearance_tags.append(tag.name)
            elif tag.type == 'personality':
                personality_tags.append(tag.name)
            else:
                other_tags.append(tag.name)
        
        print("外貌相关标签 (type='appearance'):")
        for tag in appearance_tags:
            print(f"  - {tag}")
        print()
        
        print("性格相关标签 (type='personality'):")
        for tag in personality_tags:
            print(f"  - {tag}")
        print()
        
        if other_tags:
            print("其他标签:")
            for tag in other_tags:
                print(f"  - {tag} (type: {tag.type})")
            print()
        
        print("=" * 50)
        print("总结:")
        print(f"外貌标签: {len(appearance_tags)} 个")
        print(f"性格标签: {len(personality_tags)} 个")
        print(f"其他标签: {len(other_tags)} 个")
        
        if len(personality_tags) == 0:
            print("\n⚠️ 警告: 没有找到性格相关标签！")
            print("请检查数据库中的标签type字段是否正确设置。")
            print("性格标签应该设置 type='personality'")

if __name__ == "__main__":
    check_tags() 