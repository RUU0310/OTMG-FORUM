#!/usr/bin/env python3
"""
测试幻想聊天API的脚本
"""

import requests
import json

def test_fantasy_chat_api():
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
        print("🧪 测试幻想聊天API...")
        
        # 发送请求
        response = requests.post(
            'http://localhost:5000/api/fantasy-chat',
            json=test_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("✅ API测试成功！")
                print(f"AI回复: {result.get('reply')}")
            else:
                print(f"❌ API测试失败: {result.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"错误内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 请确保Flask服务器正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def test_health_check():
    """测试健康检查接口"""
    
    try:
        print("\n🏥 测试健康检查接口...")
        response = requests.get('http://localhost:5000/api/fantasy-chat/health')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"健康检查失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试幻想聊天API...")
    print("=" * 50)
    
    test_health_check()
    test_fantasy_chat_api()
    
    print("\n" + "=" * 50)
    print("测试完成！") 