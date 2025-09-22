#!/usr/bin/env python3
import http.server
import socketserver
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
    
    def _process_path(self):
        # Если запрашиваем корень, возвращаем index.html
        if self.path == '/':
            self.path = '/index.html'
        
            # Убираем префикс /uk-UA/ и перенаправляем на корневые файлы
            new_path = self.path[7:]  # Убираем "/uk-UA/"
            if new_path in ['login.html', 'password.html', 'index.html']:
                self.path = '/' + new_path
            elif new_path == '' or new_path == '/':
                self.path = '/index.html'

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