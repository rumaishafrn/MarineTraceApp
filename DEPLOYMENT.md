# Deployment Guide - MarineTrace

## Option 1: Deploy to Vercel (Frontend) + Railway (Backend)

### Backend - Railway

1. Create account di [Railway.app](https://railway.app)

2. Install Railway CLI:
```bash
npm install -g @railway/cli
railway login
```

3. Deploy backend:
```bash
cd backend
railway init
railway up
```

4. Add environment variables di Railway dashboard:
   - Tidak ada env vars khusus untuk setup basic

5. Railway akan memberikan URL, contoh: `https://your-app.railway.app`

### Frontend - Vercel

1. Update API endpoint di `frontend/src/components/`:
   
   Buat file `frontend/src/config.js`:
   ```javascript
   export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
   ```

2. Update import di TrackingPage.jsx dan DetectionPage.jsx:
   ```javascript
   import { API_URL } from '../config'
   
   // Ganti '/api/...' menjadi:
   axios.post(`${API_URL}/api/track`, ...)
   ```

3. Deploy ke Vercel:
   ```bash
   cd frontend
   npm run build
   npx vercel
   ```

4. Set environment variable di Vercel:
   - `VITE_API_URL` = `https://your-backend.railway.app`

## Option 2: Deploy to Single Server (VPS)

### Menggunakan DigitalOcean/AWS/GCP

1. Setup server Ubuntu 22.04

2. Install dependencies:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & Node.js
sudo apt install python3 python3-pip nodejs npm -y

# Install PM2 for process management
sudo npm install -g pm2
```

3. Clone repository:
```bash
git clone https://github.com/yourusername/marine-trace.git
cd marine-trace
```

4. Setup backend:
```bash
cd backend
pip3 install -r requirements.txt
pm2 start app.py --name marine-trace-api --interpreter python3
pm2 save
```

5. Setup frontend:
```bash
cd ../frontend
npm install
npm run build

# Serve with nginx or PM2
pm2 serve dist 5173 --name marine-trace-web --spa
pm2 save
```

6. Setup Nginx reverse proxy (optional):
```nginx
# /etc/nginx/sites-available/marine-trace
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/marine-trace /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Option 3: Docker Deployment

### Create Dockerfiles

**Backend Dockerfile:**
```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**Frontend Dockerfile:**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend/models:/app/models
      - ./backend/uploads:/app/uploads
      - ./backend/results:/app/results
      - ./backend/static:/app/static
    environment:
      - FLASK_ENV=production

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:5000
```

**Deploy dengan Docker:**
```bash
docker-compose up -d
```

## Option 4: Heroku Deployment

### Backend - Heroku

1. Create `Procfile` in backend/:
```
web: python app.py
```

2. Create `runtime.txt`:
```
python-3.10.12
```

3. Deploy:
```bash
cd backend
heroku create marine-trace-api
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a marine-trace-api
git push heroku main
```

### Frontend - Netlify/Vercel

Same as Option 1

## Important Notes for Production

### 1. Security

- [ ] Enable CORS properly
- [ ] Add rate limiting
- [ ] Use HTTPS
- [ ] Validate file uploads
- [ ] Sanitize inputs
- [ ] Use environment variables for secrets

### 2. Performance

- [ ] Optimize YOLO model (quantization)
- [ ] Add image compression
- [ ] Use CDN for static assets
- [ ] Enable caching
- [ ] Add database indexes

### 3. Monitoring

- [ ] Add logging (Sentry, LogRocket)
- [ ] Monitor API performance
- [ ] Track model inference time
- [ ] Database backups

### 4. Database

For production, consider upgrading to PostgreSQL:

```python
# Replace SQLite with PostgreSQL in app.py
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
```

## GitHub Setup

```bash
# Initialize git
git init

# Add files
git add .
git commit -m "Initial commit - MarineTrace Application"

# Create repository on GitHub
# Then:
git remote add origin https://github.com/yourusername/marine-trace.git
git branch -M main
git push -u origin main
```

## Cost Estimates

### Free Tier Options:
- **Railway**: 500 hours/month free
- **Vercel**: Unlimited for personal projects
- **Netlify**: 100GB bandwidth/month
- **Heroku**: 550-1000 dyno hours/month (with GitHub Student)

### Paid Options (Approximate):
- **DigitalOcean VPS**: $6-12/month
- **AWS EC2**: $5-20/month
- **Google Cloud**: $10-30/month

## Support

Untuk pertanyaan deployment, buka issue di GitHub repository atau contact team penelitian.
