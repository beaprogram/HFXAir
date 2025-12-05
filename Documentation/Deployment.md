# HFXAIR Flask Application - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Nginx Reverse Proxy Setup](#nginx-reverse-proxy-setup)
6. [Testing the Deployment](#testing-the-deployment)
7. [Service Management](#service-management)
8. [Troubleshooting](#troubleshooting)
9. [Automated Deployment (Optional)](#automated-deployment-optional)

---

## Prerequisites

### Required Software
- Ubuntu 24.04 Server
- Python 3.10+
- Git
- Nginx
- Access to college database server (db-5308.cs.dal.ca)

### Server Information
- **VM IP:** 172.17.1.217
- **Application Port:** 5000 (internal)
- **Public Port:** 80 (via Nginx)
- **Database Server:** db-5308.cs.dal.ca:3306

---

## Environment Setup

### Step 1: Connect to the VM

```bash
ssh student@172.17.1.217
```

### Step 2: Create Python Virtual Environment

```bash
# Navigate to home directory
cd ~

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Explanation:** A virtual environment isolates Python dependencies for this project, preventing conflicts with system packages.

### Step 3: Clone the Repository

```bash
# Clone from GitLab (if not already present)
cd ~
git clone git@git.cs.dal.ca:courses/2025-Fall/csci-5308/group01.git HFXAIR

# Navigate to repository
cd ~/HFXAIR/group01

# Ensure you're on the main branch
git checkout main
git pull origin main
```

---

## Database Configuration

### Step 4: Configure Environment Variables

```bash
# Navigate to flask_app directory
cd ~/HFXAIR/group01/flask_app

# Check .env file exists and has correct configuration
cat .env
```

**Expected .env content:**
```ini
FLASK_ENV=production

DATABASE_URL=jdbc:mariadb://db-5308.cs.dal.ca:3306/CSCI5308_1_DEVINT
DB_HOST=db-5308.cs.dal.ca
DB_NAME=CSCI5308_1_DEVINT
DB_USER=CSCI5308_1_DEVINT_USER
DB_PASSWORD=Pohcoo5tig

AIRPORT_NAME=Halifax (YHZ)
```

**Explanation:** The `.env` file stores sensitive configuration including database credentials. Never commit this file to Git.

### Step 5: Test Database Connection

```bash
# Verify database connectivity
python test_db_connection.py
```

**Expected output:**
```
✓ Connected successfully!
✓ MariaDB/MySQL version: 10.11.11-MariaDB-0+deb12u1
✓ Flights table exists with 13 rows
✓ Database connection test passed!
```

**Explanation:** This confirms your application can reach the college database server and access required tables.

---

## Application Deployment

### Step 6: Install Python Dependencies

```bash
# Ensure virtual environment is activated
source ~/venv/bin/activate

# Navigate to flask_app directory
cd ~/HFXAIR/group01/flask_app

# Install all required packages
pip install -r requirements.txt

# Install Gunicorn (WSGI server for production)
pip install gunicorn
```

**Explanation:** 
- `requirements.txt` lists all Python packages needed by the application
- Gunicorn is a production-grade WSGI server that serves Flask applications
- Never use Flask's built-in development server in production

### Step 7: Create Systemd Service

Systemd will manage the application lifecycle (start, stop, restart, auto-start on boot).

```bash
# Create service file
sudo nano /etc/systemd/system/hfxair.service
```

**Paste this configuration:**
```ini
[Unit]
Description=HFXAIR Flask Application
After=network.target

[Service]
User=student
Group=student
WorkingDirectory=/home/student/HFXAIR/group01
Environment="PATH=/home/student/venv/bin"
ExecStart=/home/student/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 flask_app.app:app

[Install]
WantedBy=multi-user.target
```

**Configuration explained:**
- `After=network.target`: Start service after network is available
- `WorkingDirectory`: Set the working directory to repository root
- `Environment="PATH=..."`: Use virtual environment's Python packages
- `--bind 0.0.0.0:5000`: Listen on all network interfaces, port 5000
- `--workers 4`: Run 4 worker processes for handling concurrent requests
- `flask_app.app:app`: Import path to Flask application object

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 8: Start and Enable the Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Start the service
sudo systemctl start hfxair

# Enable auto-start on boot
sudo systemctl enable hfxair

# Check service status
sudo systemctl status hfxair
```

**Expected output:**
```
● hfxair.service - HFXAIR Flask Application
     Loaded: loaded (/etc/systemd/system/hfxair.service; enabled)
     Active: active (running) since [timestamp]
   Main PID: [pid] (gunicorn)
      Tasks: 5 (limit: 4722)
     Memory: ~120M
```

**Explanation:** 
- `daemon-reload`: Tells systemd to reload configuration files
- `start`: Starts the service immediately
- `enable`: Configures service to start automatically on system boot
- You should see "active (running)" and 5 tasks (1 master + 4 workers)

---

## Nginx Reverse Proxy Setup

### Step 9: Configure Nginx

Nginx acts as a reverse proxy, forwarding requests from port 80 (HTTP) to your application on port 5000.

**Why use Nginx?**
- Handles static files efficiently
- Provides load balancing
- Adds security layer
- Port 80 is standard HTTP port (no need to specify port in URL)

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/hfxair
```

**Paste this configuration:**
```nginx
server {
    listen 80;
    server_name 172.17.1.217;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Configuration explained:**
- `listen 80`: Accept connections on port 80 (standard HTTP)
- `server_name`: Your VM's IP address
- `proxy_pass`: Forward requests to Flask app on localhost:5000
- `proxy_set_header`: Preserve original client information in forwarded requests

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 10: Enable Nginx Site

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/hfxair /etc/nginx/sites-enabled/

# Test Nginx configuration for syntax errors
sudo nginx -t

# Restart Nginx to apply changes
sudo systemctl restart nginx
```

**Expected output from `nginx -t`:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**Explanation:** 
- Sites in `sites-enabled` are active configurations
- Always test configuration before restarting to catch errors
- Restart applies the new configuration

---

## Testing the Deployment

### Step 11: Test Locally on VM

```bash
# Test root endpoint
curl http://localhost:5000/

# Expected response:
# {"message": "Welcome to HFX AIR, your local airport app!"}

# Verify port 5000 is listening
sudo ss -tulnp | grep :5000

# Expected: Shows 5 gunicorn processes listening on port 5000
```

### Step 12: Test External Access

**From your local machine (laptop):**

```bash
# Test via browser
# Open: http://172.17.1.217/

# Or test via curl
curl http://172.17.1.217/
```

**Expected response:**
```json
{
  "message": "Welcome to HFX AIR, your local airport app!"
}
```

### Step 13: Test API Endpoints

```bash
# Test login endpoint (requires POST with JSON)
curl -X POST http://172.17.1.217/login \
  -H "Content-Type: application/json" \
  -d '{"flight_number":"FL123","ticket_number":"TK456"}'

# Expected response (for invalid credentials):
# {"error": "Invalid flight or ticket"}
```

**Note:** The 401 error is expected if the flight/ticket combination doesn't exist in the database.

---

## Service Management

### Common Commands

```bash
# Check service status
sudo systemctl status hfxair

# View live logs (follow mode)
sudo journalctl -u hfxair -f

# View last 50 log lines
sudo journalctl -u hfxair -n 50

# Restart service (after code changes)
sudo systemctl restart hfxair

# Stop service
sudo systemctl stop hfxair

# Start service
sudo systemctl start hfxair

# Disable auto-start on boot
sudo systemctl disable hfxair

# Enable auto-start on boot
sudo systemctl enable hfxair
```

### Checking Running Processes

```bash
# View gunicorn processes
ps aux | grep gunicorn

# Check what's listening on port 5000
sudo ss -tulnp | grep :5000

# Check Nginx status
sudo systemctl status nginx
```

---

## Troubleshooting

### Issue 1: Service Fails to Start

**Symptoms:** Service shows "failed" status

**Diagnosis:**
```bash
# Check detailed logs
sudo journalctl -u hfxair -n 50 --no-pager

# Common errors:
# - "ModuleNotFoundError": Wrong working directory or Python path
# - "Address already in use": Port 5000 is occupied
# - Database connection errors: Check .env file
```

**Solutions:**

**For ModuleNotFoundError:**
```bash
# Verify service file has correct paths
sudo nano /etc/systemd/system/hfxair.service
# Ensure WorkingDirectory=/home/student/HFXAIR/group01
# Ensure ExecStart uses correct module path: flask_app.app:app
```

**For port already in use:**
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 [PID]

# Restart service
sudo systemctl restart hfxair
```

### Issue 2: Worker Timeouts

**Symptoms:** Logs show "WORKER TIMEOUT" or "Worker was sent SIGKILL"

**Causes:**
- Application code hanging on certain requests
- Database queries taking too long
- Memory issues

**Solutions:**
```bash
# Increase worker timeout in service file
sudo nano /etc/systemd/system/hfxair.service

# Modify ExecStart line to add timeout:
ExecStart=/home/student/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 flask_app.app:app

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart hfxair
```

### Issue 3: Database Connection Failed

**Symptoms:** Error "Can't connect to MySQL server"

**Diagnosis:**
```bash
# Test database connectivity
ping -c 3 db-5308.cs.dal.ca

# Test database connection from Python
cd ~/HFXAIR/group01/flask_app
python test_db_connection.py
```

**Solutions:**
- Verify `.env` file has correct credentials
- Ensure college network connectivity
- Check if database server is accessible from VM

### Issue 4: 502 Bad Gateway from Nginx

**Symptoms:** Browser shows "502 Bad Gateway"

**Diagnosis:**
```bash
# Check if Flask app is running
sudo systemctl status hfxair

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

**Solutions:**
```bash
# Restart Flask service
sudo systemctl restart hfxair

# Restart Nginx
sudo systemctl restart nginx
```

### Issue 5: Can't Access from External Network

**Symptoms:** curl http://172.17.1.217/ hangs or times out

**Solutions:**
```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check if port 80 is listening
sudo ss -tulnp | grep :80

# Check firewall
sudo ufw status

# If firewall is active, allow port 80
sudo ufw allow 80/tcp
```

---

## Deployment Updates

### Manual Update Process

When you push changes to the main branch:

```bash
# SSH into VM
ssh student@172.17.1.217

# Activate virtual environment
source ~/venv/bin/activate

# Navigate to repository
cd ~/HFXAIR/group01

# Pull latest changes
git pull origin main

# Install any new dependencies
pip install -r flask_app/requirements.txt

# Restart service to apply changes
sudo systemctl restart hfxair

# Verify deployment
curl http://localhost:5000/

# Check logs for errors
sudo journalctl -u hfxair -n 20
```

---

## Architecture Overview

```
┌─────────────────┐
│   User Browser  │
│  (Your Laptop)  │
└────────┬────────┘
         │ HTTP Request
         │ http://172.17.1.217/
         ▼
┌─────────────────────────────┐
│     Nginx (Port 80)         │
│  Reverse Proxy Server       │
└────────┬────────────────────┘
         │ Forwards to
         │ localhost:5000
         ▼
┌─────────────────────────────┐
│  Gunicorn (Port 5000)       │
│  - 1 Master Process         │
│  - 4 Worker Processes       │
└────────┬────────────────────┘
         │ Runs
         ▼
┌─────────────────────────────┐
│  Flask Application          │
│  (HFXAIR Backend)           │
└────────┬────────────────────┘
         │ Database Queries
         ▼
┌─────────────────────────────┐
│  MariaDB Database Server    │
│  db-5308.cs.dal.ca:3306     │
│  CSCI5308_1_DEVINT          │
└─────────────────────────────┘
```

---

## Security Considerations

### 1. Environment Variables
- Never commit `.env` file to Git
- Use `.gitignore` to exclude sensitive files
- Rotate database passwords periodically

### 2. Firewall Configuration
```bash
# If using UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw enable
```

### 3. Systemd Service Security
- Service runs as `student` user (not root)
- Limited file system access
- Isolated from other services

---

## Performance Optimization

### Gunicorn Worker Configuration

Current setup: 4 workers

**Formula for optimal workers:**
```
workers = (2 * CPU cores) + 1
```

**To adjust:**
```bash
sudo nano /etc/systemd/system/hfxair.service

# Change --workers 4 to desired number
ExecStart=/home/student/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 8 flask_app.app:app

# Restart
sudo systemctl daemon-reload
sudo systemctl restart hfxair
```

---

## Monitoring

### Check System Resources

```bash
# Memory usage
free -h

# Disk space
df -h

# CPU usage
top

# Application memory usage
ps aux | grep gunicorn
```

### Application Health Check

```bash
# Create health check endpoint test
curl http://localhost:5000/

# Should return JSON response within 1 second
```

---

## Backup and Recovery

### Backup Configuration Files

```bash
# Create backup directory
mkdir -p ~/backups

# Backup service file
sudo cp /etc/systemd/system/hfxair.service ~/backups/

# Backup nginx config
sudo cp /etc/nginx/sites-available/hfxair ~/backups/

# Backup .env file
cp ~/HFXAIR/group01/flask_app/.env ~/backups/
```

### Disaster Recovery

If deployment fails catastrophically:

```bash
# Stop broken service
sudo systemctl stop hfxair

# Remove service file
sudo rm /etc/systemd/system/hfxair.service

# Kill any stuck processes
sudo pkill -9 -f gunicorn

# Restore from backup
sudo cp ~/backups/hfxair.service /etc/systemd/system/

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl start hfxair
```

---

## Appendix: Complete Command Reference

### Initial Setup
```bash
ssh student@172.17.1.217
cd ~
python3 -m venv venv
source venv/bin/activate
git clone [repository] HFXAIR
cd HFXAIR/group01
git checkout main
```

### Installation
```bash
source ~/venv/bin/activate
cd ~/HFXAIR/group01/flask_app
pip install -r requirements.txt
pip install gunicorn
python test_db_connection.py
```

### Service Configuration
```bash
sudo nano /etc/systemd/system/hfxair.service
sudo systemctl daemon-reload
sudo systemctl start hfxair
sudo systemctl enable hfxair
sudo systemctl status hfxair
```

### Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/hfxair
sudo ln -s /etc/nginx/sites-available/hfxair /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Testing
```bash
curl http://localhost:5000/
curl http://172.17.1.217/
sudo systemctl status hfxair
sudo journalctl -u hfxair -f
```

### Updates
```bash
cd ~/HFXAIR/group01
git pull origin main
sudo systemctl restart hfxair
```