#!/usr/bin/env python3
"""
测试理想形象图片合成功能
"""

import requests
import json
import os

def test_ideal_character_api():
    """测试理想形象API"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试理想形象图片合成功能")
    print("=" * 50)
    
    # 测试获取素材列表
    print("1. 测试获取素材列表...")
    try:
        response = requests.get(f"{base_url}/api/ideal-character-materials")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 获取素材列表成功")
                print("可用素材:")
                for category, materials in data['materials'].items():
                    print(f"  {category}: {materials}")
            else:
                print("❌ 获取素材列表失败:", data['message'])
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n2. 测试生成理想形象图片...")
    
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
                print("✅ 生成理想形象图片成功")
                print(f"图片数据长度: {len(data['image_data'])} 字符")
                
                # 保存测试图片
                if data['image_data'].startswith('data:image/png;base64,'):
                    import base64
                    img_data = data['image_data'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    
                    test_img_path = "test_ideal_character.png"
                    with open(test_img_path, 'wb') as f:
                        f.write(img_bytes)
                    print(f"✅ 测试图片已保存到: {test_img_path}")
                else:
                    print("⚠️ 图片数据格式异常")
            else:
                print("❌ 生成理想形象图片失败:", data['message'])
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print("响应内容:", response.text)
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def check_material_directories():
    """检查素材目录结构"""
    print("\n3. 检查素材目录结构...")
    
    base_path = "static/ideal_character"
    categories = ['hair', 'eyes', 'glasses', 'aura', 'age']
    
    for category in categories:
        category_path = os.path.join(base_path, category)
        if os.path.exists(category_path):
            files = os.listdir(category_path)
            print(f"✅ {category}: {len(files)} 个文件")
            for file in files:
                if file.endswith('.png'):
                    print(f"    - {file}")
        else:
            print(f"❌ {category}: 目录不存在")

if __name__ == "__main__":
    print("🎭 理想形象图片合成功能测试")
    print("请确保后端服务器正在运行 (python app.py)")
    print()
    
    check_material_directories()
    test_ideal_character_api()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n注意事项:")
    print("1. 如果素材目录不存在或为空，图片合成会跳过缺失的图层")
    print("2. 请确保所有素材图片尺寸一致且背景透明")
    print("3. 素材文件名必须与代码中的映射表匹配") 