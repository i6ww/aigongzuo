from flask import Flask, request, jsonify, Response, session, send_from_directory
import requests
import json
import re
import base64
import time
import hashlib
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

BASE_URL = "https://www.371181668.xyz"

# 凭证存储文件路径
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')

# 从文件加载保存的凭证
def load_credentials():
    try:
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"已加载凭证，上次登录时间: {data.get('last_login', '未知')}")
                return data
    except Exception as e:
        logger.error(f"加载凭证失败: {e}")
    return None

# 保存凭证到文件
def save_credentials(username, password):
    try:
        data = {
            'username': username,
            'password': password,
            'last_login': datetime.now().isoformat()
        }
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(data, f)
        logger.info(f"凭证已保存: {username}")
        return True
    except Exception as e:
        logger.error(f"保存凭证失败: {e}")
        return False

# 清除凭证
def clear_credentials():
    try:
        if os.path.exists(CREDENTIALS_FILE):
            os.remove(CREDENTIALS_FILE)
        return True
    except Exception as e:
        logger.error(f"清除凭证失败: {e}")
        return False

# 获取保存的 API Key
def get_saved_api_key():
    creds = load_credentials()
    if creds and creds.get('api_key'):
        return creds['api_key']
    return None

# 模型列表
MODELS = {
    "1K": [
        "firefly-nano-banana-1k-16x9",
        "firefly-nano-banana-1k-1x1",
        "firefly-nano-banana-1k-21x9",
        "firefly-nano-banana-1k-3x4",
        "firefly-nano-banana-1k-4x3",
        "firefly-nano-banana-1k-4x5",
        "firefly-nano-banana-1k-5x4",
        "firefly-nano-banana-1k-9x16",
        "firefly-nano-banana-pro-1k-16x9",
        "firefly-nano-banana-pro-1k-1x1",
        "firefly-nano-banana-pro-1k-21x9",
        "firefly-nano-banana-pro-1k-3x4",
        "firefly-nano-banana-pro-1k-4x3",
        "firefly-nano-banana-pro-1k-4x5",
        "firefly-nano-banana-pro-1k-5x4",
        "firefly-nano-banana-pro-1k-9x16",
        "firefly-nano-banana2-1k-16x9",
        "firefly-nano-banana2-1k-1x1",
        "firefly-nano-banana2-1k-1x4",
        "firefly-nano-banana2-1k-1x8",
        "firefly-nano-banana2-1k-21x9",
        "firefly-nano-banana2-1k-2x3",
        "firefly-nano-banana2-1k-3x2",
        "firefly-nano-banana2-1k-3x4",
        "firefly-nano-banana2-1k-4x3",
        "firefly-nano-banana2-1k-4x5",
        "firefly-nano-banana2-1k-5x4",
        "firefly-nano-banana2-1k-8x1",
        "firefly-nano-banana2-1k-9x16",
    ],
    "2K": [
        "firefly-nano-banana-2k-16x9",
        "firefly-nano-banana-2k-1x1",
        "firefly-nano-banana-2k-21x9",
        "firefly-nano-banana-2k-3x4",
        "firefly-nano-banana-2k-4x3",
        "firefly-nano-banana-2k-4x5",
        "firefly-nano-banana-2k-5x4",
        "firefly-nano-banana-2k-9x16",
        "firefly-nano-banana-pro-2k-16x9",
        "firefly-nano-banana-pro-2k-1x1",
        "firefly-nano-banana-pro-2k-21x9",
        "firefly-nano-banana-pro-2k-3x4",
        "firefly-nano-banana-pro-2k-4x3",
        "firefly-nano-banana-pro-2k-4x5",
        "firefly-nano-banana-pro-2k-5x4",
        "firefly-nano-banana-pro-2k-9x16",
        "firefly-nano-banana2-2k-16x9",
        "firefly-nano-banana2-2k-1x1",
        "firefly-nano-banana2-2k-1x4",
        "firefly-nano-banana2-2k-1x8",
        "firefly-nano-banana2-2k-21x9",
        "firefly-nano-banana2-2k-2x3",
        "firefly-nano-banana2-2k-3x2",
        "firefly-nano-banana2-2k-3x4",
        "firefly-nano-banana2-2k-4x3",
        "firefly-nano-banana2-2k-4x5",
        "firefly-nano-banana2-2k-5x4",
        "firefly-nano-banana2-2k-8x1",
        "firefly-nano-banana2-2k-9x16",
    ],
    "4K": [
        "firefly-nano-banana-4k-16x9",
        "firefly-nano-banana-4k-1x1",
        "firefly-nano-banana-4k-21x9",
        "firefly-nano-banana-4k-3x4",
        "firefly-nano-banana-4k-4x3",
        "firefly-nano-banana-4k-4x5",
        "firefly-nano-banana-4k-5x4",
        "firefly-nano-banana-4k-9x16",
        "firefly-nano-banana-pro-4k-16x9",
        "firefly-nano-banana-pro-4k-1x1",
        "firefly-nano-banana-pro-4k-21x9",
        "firefly-nano-banana-pro-4k-3x4",
        "firefly-nano-banana-pro-4k-4x3",
        "firefly-nano-banana-pro-4k-4x5",
        "firefly-nano-banana-pro-4k-5x4",
        "firefly-nano-banana-pro-4k-9x16",
        "firefly-nano-banana2-4k-16x9",
        "firefly-nano-banana2-4k-1x1",
        "firefly-nano-banana2-4k-1x4",
        "firefly-nano-banana2-4k-1x8",
        "firefly-nano-banana2-4k-21x9",
        "firefly-nano-banana2-4k-2x3",
        "firefly-nano-banana2-4k-3x2",
        "firefly-nano-banana2-4k-3x4",
        "firefly-nano-banana2-4k-4x3",
        "firefly-nano-banana2-4k-4x5",
        "firefly-nano-banana2-4k-5x4",
        "firefly-nano-banana2-4k-8x1",
        "firefly-nano-banana2-4k-9x16",
    ],
}


@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空响应

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/models')
def get_models():
    return jsonify(MODELS)


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口"""
    logger.info("收到登录请求")
    
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Content-Type 必须为 application/json'}), 400
    
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    try:
        # 调用上游登录接口验证
        logger.info(f"正在验证用户: {username}")
        response = requests.post(
            f"{BASE_URL}/api/user/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        result = response.json()
        logger.info(f"上游响应: success={result.get('success')}, message={result.get('message')}")
        
        if result.get('success'):
            # 登录成功，保存凭证
            user_data = result.get('data', {})
            api_key = data.get('apiKey', '').strip()  # 可选：用户可以提供自己的 API Key
            
            # 如果没有提供 API Key，尝试从保存的凭证获取
            if not api_key:
                saved = load_credentials()
                if saved and saved.get('username') == username:
                    api_key = saved.get('api_key', '')
            
            creds_data = {
                'username': username,
                'password': password,
                'api_key': api_key,
                'user_info': user_data,
                'last_login': datetime.now().isoformat()
            }
            
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(creds_data, f)
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'data': {
                    'username': username,
                    'display_name': user_data.get('display_name', username),
                    'has_api_key': bool(api_key)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '用户名或密码错误')
            }), 401
            
    except requests.exceptions.Timeout:
        logger.error("登录请求超时")
        return jsonify({'success': False, 'message': '登录超时，请重试'}), 500
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接失败: {e}")
        return jsonify({'success': False, 'message': '无法连接到服务器'}), 500
    except Exception as e:
        logger.error(f"登录异常: {e}")
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """退出登录"""
    clear_credentials()
    return jsonify({'success': True, 'message': '已退出登录'})


@app.route('/api/check-login', methods=['GET'])
def check_login():
    """检查登录状态"""
    creds = load_credentials()
    if creds and creds.get('username'):
        return jsonify({
            'success': True,
            'data': {
                'username': creds.get('username'),
                'display_name': creds.get('user_info', {}).get('display_name', creds.get('username')),
                'has_api_key': bool(creds.get('api_key'))
            }
        })
    return jsonify({'success': False, 'message': '未登录'})


@app.route('/api/save-api-key', methods=['POST'])
def save_api_key():
    """保存用户的 API Key"""
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Content-Type 必须为 application/json'}), 400
    
    data = request.json
    api_key = data.get('apiKey', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'message': 'API Key 不能为空'}), 400
    
    creds = load_credentials()
    if not creds or not creds.get('username'):
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    creds['api_key'] = api_key
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(creds, f)
    
    logger.info(f"API Key 已保存 for user: {creds['username']}")
    return jsonify({'success': True, 'message': 'API Key 已保存'})


@app.route('/api/generate', methods=['POST'])
def generate():
    logger.info(f"收到生成请求")
    
    # 检查 Content-Type
    if not request.is_json:
        logger.error(f"Content-Type 不是 application/json")
        return jsonify({'error': 'Content-Type 必须为 application/json'}), 400
    
    data = request.json
    model = data.get('model')
    prompt = data.get('prompt')
    image_data = data.get('image')  # 单张图片
    images_data = data.get('images')  # 多张图片
    
    # 日志请求参数（敏感信息脱敏）
    has_image = bool(image_data or images_data)
    prompt_preview = prompt[:100] + '...' if prompt and len(prompt) > 100 else prompt
    logger.info(f"请求参数: model={model}, prompt长度={len(prompt) if prompt else 0}, 有图片={has_image}")

    if not model or not prompt:
        logger.error(f"缺少必要参数: model={model}, prompt={bool(prompt)}")
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 从服务端获取保存的 API Key
    api_key = None
    creds = load_credentials()
    if creds:
        api_key = creds.get('api_key')
    
    # 如果没有保存的 Key，返回错误提示用户配置
    if not api_key:
        logger.error("未配置 API Key")
        return jsonify({
            'error': '请先在设置中配置 API Key',
            'need_config': True,
            'message': '请登录后配置您的 API Key'
        }), 401

    try:
        # 构建消息内容
        if image_data or images_data:
            # 图生图模式
            content = [{"type": "text", "text": prompt}]
            
            # 处理单张或多张图片
            if images_data:
                # 多图模式
                for img in images_data:
                    if ',' in img:
                        image_b64 = img.split(',')[1]
                    else:
                        image_b64 = img
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})
            elif image_data:
                # 单图模式
                if ',' in image_data:
                    image_b64 = image_data.split(',')[1]
                else:
                    image_b64 = image_data
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})
            
            messages = [{"role": "user", "content": content}]
        else:
            # 文生图模式
            messages = [{"role": "user", "content": prompt}]

        # 调用API（非流式，更容易解析）
        logger.info(f"正在调用API: {BASE_URL}/v1/chat/completions, 模型: {model}")
        try:
            response = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": messages
                },
                timeout=120  # 2分钟超时
            )
            logger.info(f"API响应状态码: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            return jsonify({'error': '请求超时，请重试'}), 500
        except requests.exceptions.ConnectionError as e:
            logger.error(f"无法连接到API服务器: {e}")
            return jsonify({'error': '无法连接到API服务器'}), 500
        except Exception as e:
            logger.error(f"连接异常: {e}")
            return jsonify({'error': f'连接错误: {str(e)}'}), 500

        if response.status_code != 200:
            error_detail = response.text[:200]
            logger.error(f"API返回错误状态码: {response.status_code}, 响应: {error_detail}")
            
            # 更友好的错误提示
            if response.status_code == 401:
                return jsonify({'error': 'API Key无效或已过期，请检查后重新输入'}), 401
            elif response.status_code == 403:
                return jsonify({'error': 'API Key没有访问权限'}), 403
            elif response.status_code == 429:
                return jsonify({'error': '请求过于频繁，请稍后再试'}), 429
            else:
                return jsonify({'error': f'HTTP {response.status_code}: {error_detail}'}), response.status_code

        # 解析响应
        try:
            result = response.json()
        except Exception as e:
            logger.error(f"JSON解析失败: {e}, 响应文本: {response.text[:500]}")
            return jsonify({'error': f'响应解析失败: {str(e)}'}), 500
        
        if 'choices' not in result or not result['choices']:
            logger.error(f"API返回格式错误: {str(result)[:500]}")
            return jsonify({'error': 'API返回格式错误', 'debug': str(result)[:200]}), 500

        content = result['choices'][0]['message']['content']
        
        # 提取图片URL（支持多种格式）
        image_urls = []
        
        # Markdown格式: ![alt](url)
        image_urls.extend(re.findall(r'!\[.*?\]\((.*?)\)', content))
        
        # 纯URL格式
        image_urls.extend(re.findall(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', content, re.I))
        
        # 宽松URL匹配
        for match in re.findall(r'https?://[^\s"\')\]]+', content):
            if any(ext in match.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', 'file', 'img', 'generated']):
                if match not in image_urls:
                    image_urls.append(match)

        if image_urls:
            logger.info(f"成功提取图片数量: {len(image_urls)}")
            return jsonify({'image': image_urls[0], 'allImages': image_urls, 'content': content})
        else:
            logger.warning(f"未找到图片，内容前500字符: {content[:500]}")
            return jsonify({'error': '未找到图片', 'debug': content[:500]}), 500

    except requests.exceptions.Timeout:
        logger.error("API请求超时")
        return jsonify({'error': '请求超时，请稍后重试'}), 500
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接错误: {e}")
        return jsonify({'error': '无法连接到API服务器，请稍后重试'}), 500
    except Exception as e:
        logger.error(f"生成图片时发生错误: {e}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


# 全局错误处理器
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"未处理的异常: {e}")
    return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/api/download')
def download_image():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': '缺少URL'}), 400
    
    try:
        response = requests.get(url, timeout=30)
        return Response(
            response.content,
            mimetype=response.headers.get('Content-Type', 'image/jpeg'),
            headers={
                'Content-Disposition': f'attachment; filename=ai-image-{int(time.time())}.jpg',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    # 生产环境使用 waitress 运行时忽略此配置
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, threads=4)