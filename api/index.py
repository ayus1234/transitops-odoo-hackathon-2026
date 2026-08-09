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
    from app.main import app as real_app
except Exception:
    import traceback
    tb_init = traceback.format_exc()
    real_app = None

async def app(scope, receive, send):
    if real_app is None:
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [[b'content-type', b'text/plain; charset=utf-8']],
            })
            await send({
                'type': 'http.response.body',
                'body': f"VERCEL BOOTSTRAP ERROR:\n\n{tb_init}".encode('utf-8'),
            })
        return

    try:
        await real_app(scope, receive, send)
    except Exception:
        import traceback
        tb_runtime = traceback.format_exc()
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [[b'content-type', b'text/plain; charset=utf-8']],
            })
            await send({
                'type': 'http.response.body',
                'body': f"VERCEL RUNTIME ERROR:\n\n{tb_runtime}".encode('utf-8'),
            })
