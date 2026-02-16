# Deployment Guide

This guide outlines the steps to deploy the Marine Debris Tracking application on a Linux server (e.g., Ubuntu 22.04).

## 1. Server Prerequisites

Ensure your server has the following installed:

*   **Python 3.10+** (Recommend Miniforge or Anaconda)
*   **Node.js 18+** & **npm**
*   **Nginx** (Web Server)
*   **Git**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nginx git python3-pip python3-venv libnetcdf-dev libgdal-dev
```

## 2. Clone the Repository

```bash
cd /var/www
git clone <your-repo-url> marine-trace
cd marine-trace
```

## 3. Backend Deployment (Flask)

We will use **Gunicorn** as the WSGI server and **Systemd** to manage the process.

### Set up Python Environment

```bash
# Create virtual environment (or use conda)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Configure Gunicorn Service

Create a systemd service file: `/etc/systemd/system/marine-backend.service`

```ini
[Unit]
Description=Gunicorn instance to serve Marine Trace Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/marine-trace/MarineTraceApp/backend
Environment="PATH=/var/www/marine-trace/venv/bin"
ExecStart=/var/www/marine-trace/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start marine-backend
sudo systemctl enable marine-backend
```

## 4. Frontend Deployment (React)

We will build the React app and serve the static files via Nginx.

### Build the Application

```bash
cd /var/www/marine-trace/MarineTraceApp/frontend
npm install
npm run build
```

The build artifacts will be in the `dist` folder.

## 5. Nginx Configuration

Create an Nginx server block: `/etc/nginx/sites-available/marine-trace`

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    # Frontend (Static Files)
    location / {
        root /var/www/marine-trace/MarineTraceApp/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static Files from Backend (Simulation Results)
    location /static/simulations {
        alias /var/www/marine-trace/MarineTraceApp/backend/static/simulations;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/marine-trace /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. Environment Variables & Security

*   Ensure `DEBUG=False` in your Flask production config.
*   Set up SSL/HTTPS using Certbot (Let's Encrypt):
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your_domain.com
    ```

## 7. Maintenance

*   **Logs**: Check backend logs via `journalctl -u marine-backend`.
*   **Updates**: Pull latest code, rebuild frontend, and restart backend service.
