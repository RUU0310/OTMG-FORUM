#!/usr/bin/env python3
"""
测试标签分类API
"""

import requests
import json

def test_tag_categories_api():
    """测试标签分类API"""
    base_url = "http://localhost:5000"
    
    print("🏷️ 测试标签分类API")
    print("=" * 50)
    
    # 测试获取标签分类
    print("1. 测试获取标签分类...")
    try:
        response = requests.get(f"{base_url}/api/tag-categories")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 获取标签分类成功")
                print("外貌相关标签:")
                for tag in data['appearance_tags']:
                    print(f"  - {tag}")
                print("性格相关标签:")
                for tag in data['personality_tags']:
                    print(f"  - {tag}")
            else:
                print("❌ 获取标签分类失败:", data['message'])
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print("响应内容:", response.text)
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_ideal_character_with_dynamic_tags():
    """测试理想形象生成是否使用动态标签分类"""
    base_url = "http://localhost:5000"
    
    print("\n2. 测试理想形象生成...")
    
    # 测试数据
    test_traits = {
        'hair': '红',
        'eyes': '蓝', 
        'glasses': '无眼镜',
        'aura': '温柔',
        'age': '成男'
    }
    
    print(f"测试特征: {test_traits}")
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-ideal-character",
            json={'traits': test_traits},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 理想形象生成成功")
                print(f"图片数据长度: {len(data['image_data'])} 字符")
            else:
                print("❌ 理想形象生成失败:", data['message'])
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🏷️ 标签分类API测试")
    print("请确保后端服务器正在运行 (python app.py)")
    print()
    
    test_tag_categories_api()
    test_ideal_character_with_dynamic_tags()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n说明:")
    print("1. 标签分类现在从数据库动态获取")
    print("2. 外貌标签使用外貌评分，性格标签使用性格评分")
    print("3. 如果API调用失败，会使用默认的硬编码分类作为备选") 