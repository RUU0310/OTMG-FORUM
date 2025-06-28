from flask import Blueprint, request, jsonify
from openai import OpenAI
import json
import os
from datetime import datetime

fantasy_chat_api = Blueprint('fantasy_chat_api', __name__)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-e3be16962b18459381a1a300eea6b0d1')

@fantasy_chat_api.route('/fantasy-chat', methods=['POST'])
def fantasy_chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        character_traits = data.get('character_traits', {})
        
        if not user_message:
            return jsonify({'success': False, 'message': '消息不能为空'})
        
        if not DEEPSEEK_API_KEY:
            return jsonify({'success': False, 'message': 'API密钥未配置'})
        
        # 构建角色设定
        character_prompt = build_character_prompt(character_traits)
        
        # 构建完整的对话提示
        system_prompt = f"""你是一个基于用户偏好生成的理想角色形象。请严格按照以下设定来回复：

{character_prompt}

重要规则：
1. 始终保持角色设定的一致性
2. 回复要自然、有趣，符合角色的性格特征
3. 回复长度控制在50-150字之间
4. 不要暴露你是AI的身份
5. 用中文回复
6. 保持对话的连贯性和情感投入

现在开始与用户对话："""

        # 使用OpenAI SDK调用DeepSeek API
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=300,
            stream=False
        )
        
        ai_reply = response.choices[0].message.content.strip()
        
        # 记录对话日志
        log_chat(user_message, ai_reply, character_traits)
        
        return jsonify({
            'success': True,
            'reply': ai_reply
        })
            
    except Exception as e:
        print(f"DeepSeek API调用错误: {e}")
        return jsonify({
            'success': False,
            'message': 'AI服务暂时不可用，请稍后再试'
        })

def build_character_prompt(traits):
    """根据角色特征构建提示词"""
    prompt_parts = []
    
    # 外貌特征
    appearance_parts = []
    if traits.get('hair'):
        appearance_parts.append(f"发色：{traits['hair']}")
    if traits.get('eye'):
        appearance_parts.append(f"瞳色：{traits['eye']}")
    if traits.get('glass'):
        appearance_parts.append(f"配饰：{traits['glass']}")
    if traits.get('aura'):
        appearance_parts.append(f"气质：{traits['aura']}")
    if traits.get('age'):
        appearance_parts.append(f"年龄特征：{traits['age']}")
    
    if appearance_parts:
        prompt_parts.append(f"外貌特征：{', '.join(appearance_parts)}")
    
    # 性格特征
    personality_parts = []
    if traits.get('baseChar'):
        personality_parts.append(f"基础性格：{traits['baseChar']}")
    if traits.get('tone'):
        personality_parts.append(f"说话语气：{traits['tone']}")
    if traits.get('world'):
        personality_parts.append(f"世界观背景：{traits['world']}")
    
    if personality_parts:
        prompt_parts.append(f"性格特征：{', '.join(personality_parts)}")
    
    # 如果没有特征，使用默认设定
    if not prompt_parts:
        prompt_parts.append("你是一个温柔、善解人意的角色，说话温和有礼，会关心对方的感受。")
    
    return '\n'.join(prompt_parts)

def log_chat(user_message, ai_reply, character_traits):
    """记录对话日志"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'ai_reply': ai_reply,
            'character_traits': character_traits
        }
        
        print(f"对话日志: {json.dumps(log_entry, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"记录日志失败: {e}")

# 健康检查接口
@fantasy_chat_api.route('/fantasy-chat/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Fantasy Chat API is running',
        'api_key_configured': bool(DEEPSEEK_API_KEY)
    }) 