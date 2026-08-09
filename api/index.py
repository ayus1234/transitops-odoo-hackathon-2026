import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(parent_dir, "backend")

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
except Exception as err:
    import traceback
    tb_text = traceback.format_exc()

    async def app(scope, receive, send):
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [[b'content-type', b'text/plain; charset=utf-8']],
            })
            await send({
                'type': 'http.response.body',
                'body': f"VERCEL IMPORT ERROR:\n\n{tb_text}".encode('utf-8'),
            })
