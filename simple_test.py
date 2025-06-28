#!/usr/bin/env python3
"""
简单的标签分类测试
"""

import requests

def test_tag_categories():
    """测试标签分类API"""
    try:
        print("🧪 测试标签分类API...")
        response = requests.get('http://localhost:5000/api/tag-categories')
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ API调用成功")
                print(f"总标签数: {data['total_tags']}")
                print(f"外貌标签: {data['appearance_tags']}")
                print(f"性格标签: {data['personality_tags']}")
                print(f"其他标签: {data['other_tags']}")
                
                if len(data['personality_tags']) == 0:
                    print("\n⚠️ 问题: 没有找到性格标签！")
                    print("这解释了为什么性格评分没有被计算。")
                    print("请检查数据库中的标签type字段。")
                else:
                    print("\n✅ 找到性格标签，系统应该能正常工作")
            else:
                print("❌ API返回失败:", data['message'])
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print("响应内容:", response.text)
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_tag_categories() 