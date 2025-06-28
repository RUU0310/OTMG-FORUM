#!/usr/bin/env python3
"""
幻想聊天功能启动脚本
"""

import os
import sys
import subprocess
import importlib.util

def check_dependencies():
    """检查并安装依赖"""
    required_packages = ['flask', 'flask_cors', 'flask_sqlalchemy', 'requests', 'openai']
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    
    return True

def check_api_key():
    """检查API密钥配置"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("⚠️  警告: 未设置DEEPSEEK_API_KEY环境变量")
        print("请按以下步骤配置:")
        print("1. 访问 https://platform.deepseek.com/ 注册账号")
        print("2. 获取API密钥")
        print("3. 设置环境变量:")
        print("   Windows: set DEEPSEEK_API_KEY=your_api_key_here")
        print("   Linux/Mac: export DEEPSEEK_API_KEY=your_api_key_here")
        print("\n或者创建.env文件并添加: DEEPSEEK_API_KEY=your_api_key_here")
        
        response = input("\n是否继续启动服务？(y/n): ")
        if response.lower() != 'y':
            return False
    else:
        print(f"✅ API密钥已配置: {api_key[:10]}...")
    
    return True

def start_server():
    """启动Flask服务器"""
    print("🚀 启动幻想聊天服务...")
    
    try:
        # 启动Flask应用
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    print("✨ 幻想聊天功能启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查API密钥
    if not check_api_key():
        return
    
    print("\n🎯 所有检查完成，准备启动服务...")
    print("服务启动后，可以访问:")
    print("- 前端: http://localhost:3000")
    print("- 后端: http://localhost:5000")
    print("- 健康检查: http://localhost:5000/api/fantasy-chat/health")
    print("\n按 Ctrl+C 停止服务")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 