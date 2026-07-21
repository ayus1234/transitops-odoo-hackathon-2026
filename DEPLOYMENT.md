# Deployment Guide: TransitOps

## Prerequisites
- A PostgreSQL 15+ database instance (e.g., AWS RDS, Azure Database for PostgreSQL).
- A virtual machine or container environment (e.g., AWS EC2, DigitalOcean Droplet, Docker).
- Python 3.10+
- Node.js 18+
- Nginx or Apache (for reverse proxy and static file serving).

## 1. Database Setup
1. Create a PostgreSQL database named `transitops`.
2. Configure credentials in the backend `.env` file:
   ```env
   DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/transitops
   ```

## 2. Backend Deployment (FastAPI)
1. Clone the repository and navigate to `backend/`.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR .\venv\Scripts\activate # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run Alembic migrations:
   ```bash
   alembic upgrade head
   ```
5. Setup a process manager (e.g., `systemd` or `pm2`) to run Uvicorn:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   ```

## 3. Frontend Deployment (Vite / React)
1. Navigate to `frontend/`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Build the application for production:
   ```bash
   npm run build
   ```
4. The output will be in `frontend/dist`.

## 4. Web Server Configuration (Nginx)
Configure Nginx to serve the static frontend files and reverse proxy API requests to the FastAPI backend.

```nginx
server {
    listen 80;
    server_name transitops.yourdomain.com;

    # Serve Frontend
    location / {
        root /path/to/transitops/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Reverse Proxy Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. Secure the site with SSL/TLS (e.g., using Certbot/Let's Encrypt).
