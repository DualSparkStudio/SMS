# Deployment Guide

## Option 1: Docker (Recommended)

### Prerequisites
- Docker & Docker Compose installed

### Steps
```bash
git clone <repository>
cd TextGuard
docker-compose up --build -d
```

Access:
- Frontend: http://localhost
- API: http://localhost/api/
- Admin: http://localhost/admin/

### Create Admin User
```bash
docker-compose exec backend python manage.py createsuperuser
```

---

## Option 2: Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py train_models
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Option 3: AWS EC2

1. Launch Ubuntu EC2 instance (t3.medium recommended)
2. Install Docker:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose
   ```
3. Clone project and run `docker-compose up -d`
4. Configure Security Group: ports 80, 443, 8000
5. Set up domain with Route 53 (optional)
6. Add SSL with Let's Encrypt + Certbot

### Environment Variables (Production)
```
DEBUG=False
SECRET_KEY=<strong-random-key>
USE_SQLITE=False
DB_HOST=<rds-endpoint>
DB_NAME=hsds_db
DB_USER=hsds_user
DB_PASSWORD=<secure-password>
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## Option 4: Render / Railway

### Backend (Render)
1. Create Web Service from GitHub repo
2. Build: `pip install -r backend/requirements.txt`
3. Start: `cd backend && python manage.py migrate && gunicorn hsds_project.wsgi:application`
4. Add MySQL database addon

### Frontend (Render Static Site)
1. Build: `cd frontend && npm install && npm run build`
2. Publish directory: `frontend/dist`
3. Set `VITE_API_URL` to backend URL

---

## MySQL Setup (Production)

```sql
CREATE DATABASE hsds_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hsds_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON hsds_db.* TO 'hsds_user'@'%';
FLUSH PRIVILEGES;
```

Update `.env`:
```
USE_SQLITE=False
DB_NAME=hsds_db
DB_USER=hsds_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=3306
```

---

## Nginx SSL Configuration

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
    }
}
```

---

## Post-Deployment Checklist

- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure MySQL
- [ ] Run migrations
- [ ] Train ML models
- [ ] Create superuser
- [ ] Configure CORS origins
- [ ] Set up SSL/HTTPS
- [ ] Configure backup for database
- [ ] Test all API endpoints
