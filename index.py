import os
import sys

# Add the backend directory to Python's path so 'from app...' imports work
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Vercel needs to see `app` defined at the top level
async def app(scope, receive, send):
    try:
        # Import the real FastAPI app on demand
        from app.main import app as real_app
        await real_app(scope, receive, send)
    except Exception as e:
        # If it crashes, return the Python traceback to the browser!
        import traceback
        error_msg = traceback.format_exc().encode('utf-8')
        
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [
                    [b'content-type', b'text/plain'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': b"Vercel Serverless Crash Report:\n\n" + error_msg,
            })
