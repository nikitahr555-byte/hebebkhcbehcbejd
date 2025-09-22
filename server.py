
#!/usr/bin/env python3
import http.server
import socketserver
import json
import os

PORT = 5000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем заголовки для предотвращения кеширования
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        self._process_path()
        return super().do_GET()
    
    def do_HEAD(self):
        self._process_path()
        return super().do_HEAD()
    
    def do_POST(self):
        # Обробляємо POST запити до API
        if self.path.startswith('/bapi/'):
            self._send_json_error({"error": "API not available", "code": 404})
        else:
            self._send_json_error({"error": "Method not allowed", "code": 405})
    
    def _send_json_error(self, error_data):
        """Відправляє JSON відповідь з помилкою"""
        response = json.dumps(error_data).encode('utf-8')
        self.send_response(200)  # Відправляємо 200 для уникнення помилок в браузері
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def _process_path(self):
        # Если запрашиваем корень, возвращаем index.html
        if self.path == '/':
            self.path = '/index.html'
            return
        
        # Убираем префикс /uk-UA/ если он есть и перенаправляем на корневые ресурсы
        if self.path.startswith('/uk-UA/'):
            new_path = self.path[7:]  # Убираем "/uk-UA/"
            
            # Для пустого пути после uk-UA
            if new_path == '' or new_path == '/':
                self.path = '/index.html'
            else:
                # Для всех ресурсов просто убираем префикс uk-UA
                self.path = '/' + new_path

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Добавляем SO_REUSEADDR для избежания "Address already in use"
    class ReuseAddrTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    with ReuseAddrTCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Сервер запущен на http://0.0.0.0:{PORT}")
        print("Нажмите Ctrl+C для остановки сервера")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
