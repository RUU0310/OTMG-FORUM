# 幻想聊天功能配置说明

## 功能概述
基于用户偏好数据生成理想形象，并通过DeepSeek API实现AI对话功能。

## 配置步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置DeepSeek API密钥
1. 访问 https://platform.deepseek.com/ 注册账号
2. 获取API密钥
3. 设置环境变量（可选，代码中已包含默认密钥）：
   ```bash
   # Windows
   set DEEPSEEK_API_KEY=your_api_key_here
   
   # Linux/Mac
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

### 3. 启动服务
```bash
python app.py
```

## 功能特性

### 理想形象生成
- 基于用户对角色外貌的评分数据
- 分析用户偏好的发色、瞳色、配饰、气质、年龄等特征
- 生成个性化的理想形象描述

### AI对话功能
- 根据用户偏好的性格特征（基础性格、语气、世界观）
- 使用OpenAI SDK调用DeepSeek API生成符合角色设定的回复
- 保持对话的连贯性和角色一致性

### 技术实现
- 前端：Vue 3 + Element Plus
- 后端：Flask + SQLAlchemy
- AI服务：DeepSeek Chat API (通过OpenAI SDK)
- 数据来源：用户角色评分和标签偏好

## API接口

### POST /api/fantasy-chat
生成AI回复

请求体：
```json
{
  "message": "用户消息",
  "character_traits": {
    "hair": "发色",
    "eye": "瞳色",
    "glass": "配饰",
    "aura": "气质",
    "age": "年龄特征",
    "baseChar": "基础性格",
    "tone": "语气",
    "world": "世界观倾向"
  }
}
```

响应：
```json
{
  "success": true,
  "reply": "AI回复内容"
}
```

### GET /api/fantasy-chat/health
健康检查接口

## 技术更新

### 使用OpenAI SDK
- 替换了原来的requests直接调用
- 使用标准的OpenAI SDK接口
- 更好的错误处理和类型安全
- 支持流式响应（当前未启用）

### API调用方式
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "系统提示"},
        {"role": "user", "content": "用户消息"}
    ],
    temperature=0.8,
    max_tokens=300,
    stream=False
)
```

## 注意事项
1. 确保有足够的DeepSeek API额度
2. API调用有30秒超时限制
3. 建议在生产环境中使用环境变量管理API密钥
4. 对话日志会记录到控制台，可根据需要保存到数据库
5. 使用OpenAI SDK提供更好的稳定性和兼容性 