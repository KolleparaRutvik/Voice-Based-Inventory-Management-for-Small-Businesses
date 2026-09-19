# 🚀 DukaanSetu — Complete Production Deployment Guide

This guide provides step-by-step instructions to deploy the **DukaanSetu** voice-first inventory application to production.

---

## 📑 Deployment Options

Choose the deployment strategy that best matches your infrastructure:

- [Method 1: Cloud PaaS (Render + Vercel)](#-method-1-cloud-paas-render--vercel---easiest--free) *(Recommended & Easiest)*
- [Method 2: Docker & Docker Compose](#-method-2-docker--docker-compose-any-vps--cloud-vm) *(Containers / AWS EC2 / DigitalOcean)*
- [Method 3: Native Ubuntu VPS (Nginx + Gunicorn + Systemd)](#-method-3-native-ubuntu-vps-systemd--nginx--ssl) *(Self-hosted / Dedicated server)*

---

## 🔑 Pre-Deployment Checklist: Environment Variables

Before deploying, ensure you have your API keys and credentials ready:

### Backend Variables (`backend/.env`)

| Variable | Description | Example / Source |
| :--- | :--- | :--- |
| `FLASK_ENV` | Application environment | `production` |
| `FLASK_DEBUG` | Flask debug flag | `0` |
| `PORT` | Web port | `5000` (or injected by platform) |
| `SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon public key | `sb_publishable_...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role key | `sb_secret_...` |
| `DATABASE_URL` | Supabase PostgreSQL URI | `postgresql://postgres.xxx:password@host:6543/postgres` |
| `GEMINI_API_KEY` | Google Gemini API key | From [Google AI Studio](https://aistudio.google.com/) |
| `SECRET_KEY` | Flask session encryption | Random 32+ character string |

### Frontend Variables (`frontend/.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Deployed backend URL | `https://dukaansetu-api.onrender.com` |
| `VITE_SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase Anon public key | `sb_publishable_...` |

---

## ☁️ Method 1: Cloud PaaS (Render + Vercel) — (Easiest & Free)

### Step 1: Deploy Backend to Render (or Railway)
1. Push your repository to GitHub.
2. Sign in to [Render.com](https://render.com).
3. Click **New +** → **Blueprint** and select your repository (Render will automatically detect `render.yaml`).
   *Alternatively, create a **Web Service**:*
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT run:app --workers 2 --threads 4 --timeout 120`
4. Under **Environment Variables**, add the keys from the checklist above.
5. Click **Deploy Web Service**.
6. Copy your public API URL (e.g., `https://dukaansetu-api.onrender.com`).

---

### Step 2: Deploy Frontend to Vercel (or Netlify)
1. Sign in to [Vercel.com](https://vercel.com).
2. Click **Add New...** → **Project** and import your repository.
3. Configure the project settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Under **Environment Variables**, set:
   - `VITE_API_BASE_URL`: Paste your Render backend URL (e.g., `https://dukaansetu-api.onrender.com`).
   - `VITE_SUPABASE_URL`: Your Supabase URL.
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase Anon Key.
5. Click **Deploy**.
6. Vercel automatically honors `frontend/vercel.json` for client-side SPA routing.

---

## 🐳 Method 2: Docker & Docker Compose (Any VPS / Cloud VM)

Deploy both backend and frontend as isolated containers on any Linux / cloud server (AWS EC2, DigitalOcean, Hetzner, GCP Compute Engine).

### 1. Clone the repository on your server
```bash
git clone https://github.com/KolleparaRutvik/Voice-Based-Inventory-Management-for-Small-Businesses.git
cd Voice-Based-Inventory-Management-for-Small-Businesses
```

### 2. Create the environment file
Create `.env` in the root directory:
```bash
cp backend/.env.example .env
nano .env
```
Fill in your `SUPABASE_URL`, `DATABASE_URL`, `GEMINI_API_KEY`, etc.

### 3. Build and launch containers
```bash
# Build and start all services in the background
docker compose up --build -d

# Verify running containers
docker compose ps

# Inspect logs
docker compose logs -f
```

- Frontend will be accessible at: `http://YOUR_SERVER_IP`
- Backend API will be accessible at: `http://YOUR_SERVER_IP:5000`

---

## 🖥️ Method 3: Native Ubuntu VPS (Systemd + Nginx + SSL)

### 1. Install System Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git
```

### 2. Set Up Backend with Gunicorn and Systemd
```bash
cd /var/www
sudo git clone https://github.com/KolleparaRutvik/Voice-Based-Inventory-Management-for-Small-Businesses.git dukaansetu
cd /var/www/dukaansetu/backend

# Create virtualenv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create systemd service `/etc/systemd/system/dukaansetu.service`:
```ini
[Unit]
Description=DukaanSetu Gunicorn Backend Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/dukaansetu/backend
EnvironmentFile=/var/www/dukaansetu/backend/.env
ExecStart=/var/www/dukaansetu/backend/venv/bin/gunicorn --bind 127.0.0.1:5000 run:app --workers 2 --threads 4 --timeout 120

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start dukaansetu
sudo systemctl enable dukaansetu
```

### 3. Build Frontend
```bash
cd /var/www/dukaansetu/frontend
npm install
npm run build
```

### 4. Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/dukaansetu`:
```nginx
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;

    # Frontend Single Page App
    location / {
        root /var/www/dukaansetu/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Reverse Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/dukaansetu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Secure with Free HTTPS (Let's Encrypt)
```bash
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

---

## 🧪 Post-Deployment Verification

1. **Check Backend Health:**
   ```bash
   curl -I https://api.yourdomain.com/api/health
   # Expected: HTTP/1.1 200 OK
   ```

2. **Verify Database Connection:**
   Visit `https://api.yourdomain.com/api/products` with your auth token.

3. **Verify Voice & Festival API:**
   Visit `https://api.yourdomain.com/api/festivals/upcoming` to verify that the festival demand dataset loaded properly.

4. **Verify Frontend Single Page Routing:**
   In your browser, visit `https://yourdomain.com/voice` and hit **Refresh** (F5). It should stay on the Voice Assistant page without returning a 404.
