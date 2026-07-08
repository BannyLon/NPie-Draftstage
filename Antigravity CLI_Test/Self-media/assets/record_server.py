import http.server, socketserver, os, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save-video':
            ct = self.headers.get('Content-Type', '')
            if 'multipart/form-data' in ct:
                _, pd = ct.split('boundary=', 1)
                boundary = pd.strip().encode()
                body = self.rfile.read(int(self.headers['Content-Length']))
                parts = body.split(b'--' + boundary)
                for part in parts:
                    if b'video/webm' in part:
                        idx = part.find(b'\r\n\r\n')
                        if idx >= 0:
                            data = part[idx+4:].rstrip(b'\r\n--')
                            out = '/Users/habhy/Documents/NPIE-program/Codex_Project/Self-media/assets/obsidian-captured.webm'
                            with open(out, 'wb') as f:
                                f.write(data)
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(b'OK')
                            sys.stdout.write(f'\nVIDEO SAVED: {len(data)} bytes\n')
                            sys.stdout.flush()
                            return
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Bad request')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, fmt, *args):
        pass

os.chdir('/Users/habhy/Documents/NPIE-program/Codex_Project/Self-media/assets')
PORT = 8990
with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    sys.stdout.write(f'SERVER READY on {PORT}\n')
    sys.stdout.flush()
    httpd.serve_forever()
