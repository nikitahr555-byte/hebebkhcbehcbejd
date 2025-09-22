
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
        # Обробляємо API запити
        if self.path.startswith('/bapi/'):
            if 'banner-compliance-check' in self.path:
                self._send_json_response({"success": True, "data": {"show": False}})
            elif 'country-city-short' in self.path:
                self._send_json_response({"country": "UA", "city": "Kyiv"})
            elif 'commonConfig' in self.path:
                self._send_json_response({"success": True, "data": {}})
            elif 'complianceActionCheck' in self.path:
                self._send_json_response({"success": True, "data": {}})
            elif 'businessCheckV2' in self.path:
                self._send_json_response({"success": True, "data": {}})
            elif 'region/language' in self.path:
                self._send_json_response({"success": True, "data": {}})
            elif 'querylangMappingByKey' in self.path:
                self._send_json_response({"success": True, "data": {}})
            elif 'authcenter/auth' in self.path:
                self._send_json_response({"success": True, "data": {}})
            else:
                self._send_json_response({"success": True, "data": {}})
            return
            
        self._process_path()
        
        # Перевіряємо чи файл існує
        file_path = '.' + self.path
        if not os.path.exists(file_path) and not os.path.isdir(file_path):
            # Якщо це JS файл, повертаємо порожній JS модуль
            if self.path.endswith('.js') or '.js.' in self.path:
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                self.wfile.write(b'// Module not found')
                return
            # Якщо це JSON файл, повертаємо порожній JSON
            elif self.path.endswith('.json'):
                self._send_json_response({})
                return
        
        return super().do_GET()
    
    def do_HEAD(self):
        self._process_path()
        return super().do_HEAD()
    
    def do_POST(self):
        # Обробляємо POST запити до API
        if self.path.startswith('/bapi/'):
            self._send_json_response({"success": True, "data": {}})
        else:
            self._send_json_response({"error": "Method not allowed", "code": 405})
    
    def _send_json_response(self, data):
        """Відправляє JSON відповідь"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def do_OPTIONS(self):
        """Обробляємо OPTIONS запити для CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _process_path(self):
        # Обробляємо API запити
        if self.path.startswith('/bapi/'):
            return  # Залишаємо як є для обробки в do_GET
            
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
