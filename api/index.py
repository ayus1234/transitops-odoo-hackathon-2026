import os
import sys
import traceback

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    for base in [current_dir, parent_dir]:
        backend_path = os.path.join(base, 'backend')
        if os.path.isdir(backend_path) and backend_path not in sys.path:
            sys.path.insert(0, backend_path)

    from backend.app.main import app
except Exception as e:
    error_msg = traceback.format_exc()
    
    async def app(scope, receive, send):
        assert scope['type'] == 'http'
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': error_msg.encode('utf-8'),
        })

