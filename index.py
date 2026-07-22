try:
    from backend.app.main import app
except Exception as e:
    import traceback
    error_msg = traceback.format_exc()
    from http.server import BaseHTTPRequestHandler
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(error_msg.encode('utf-8'))
            return
        def do_POST(self): self.do_GET()
        def do_PUT(self): self.do_GET()
        def do_DELETE(self): self.do_GET()
        def do_OPTIONS(self): self.do_GET()
    app = handler
