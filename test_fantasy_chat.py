#!/usr/bin/env python3
"""
测试幻想聊天功能的脚本
"""

import requests
import json
import os

def test_fantasy_chat():
    """测试幻想聊天API"""
    
    # 测试数据
    test_data = {
        "message": "你好，今天天气怎么样？",
        "character_traits": {
            "hair": "金色",
            "eye": "蓝色",
            "glass": "无眼镜",
            "aura": "温柔",
            "age": "青年",
            "baseChar": "温柔体贴",
            "tone": "温和",
            "world": "现代"
        }
    }
    
    try:
        # 发送请求
        response = requests.post(
            'http://localhost:5000/api/fantasy-chat',
            json=test_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 测试成功！")
                print(f"AI回复: {result.get('reply')}")
            else:
                print(f"❌ 测试失败: {result.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 请确保Flask服务器正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def test_health_check():
    """测试健康检查接口"""
    
    try:
        response = requests.get('http://localhost:5000/api/fantasy-chat/health')
        print(f"健康检查状态码: {response.status_code}")
        print(f"健康检查响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"健康检查失败: {e}")

def test_direct_deepseek():
    """直接测试DeepSeek API连接"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-e3be16962b18459381a1a300eea6b0d1')
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个温柔的角色，用中文回复。"},
                {"role": "user", "content": "你好"},
            ],
            stream=False
        )
        
        print("✅ DeepSeek API连接成功！")
        print(f"测试回复: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ DeepSeek API连接失败: {e}")

if __name__ == "__main__":
    print("🧪 开始测试幻想聊天功能...")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-e3be16962b18459381a1a300eea6b0d1')
    print(f"✅ API密钥已配置: {api_key[:10]}...")
    
    print("\n1. 测试DeepSeek API直接连接:")
    test_direct_deepseek()
    
    print("\n2. 测试健康检查接口:")
    test_health_check()
    
    print("\n3. 测试幻想聊天接口:")
    test_fantasy_chat()
    
    print("\n" + "=" * 50)
    print("测试完成！") 