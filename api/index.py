import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from backend.app.main import app
except Exception as e:
    import traceback
    error_msg = traceback.format_exc()
    
    async def app(scope, receive, send):
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/plain'],
                ]
            })
            await send({
                'type': 'http.response.body',
                'body': error_msg.encode('utf-8'),
            })
