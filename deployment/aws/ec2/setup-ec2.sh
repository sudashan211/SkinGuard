#!/bin/bash
# SkinGuard Backend - EC2 Setup Script
# This script sets up a production EC2 instance for the SkinGuard backend

set -e  # Exit on error

echo "========================================="
echo "SkinGuard Backend EC2 Setup"
echo "========================================="

# Configuration
APP_DIR="/opt/skinguard"
MODELS_DIR="/opt/skinguard/models"
LOGS_DIR="/var/log/skinguard"
USER="skinguard"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    postgresql-client \
    libpq-dev \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    htop \
    vim \
    build-essential

# Install Docker (optional)
print_status "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Create application user
print_status "Creating application user..."
if ! id "$USER" &>/dev/null; then
    useradd -m -s /bin/bash $USER
    print_status "User $USER created"
else
    print_warning "User $USER already exists"
fi

# Create directories
print_status "Creating application directories..."
mkdir -p $APP_DIR $MODELS_DIR $LOGS_DIR
chown -R $USER:$USER $APP_DIR $MODELS_DIR $LOGS_DIR

# Clone repository
print_status "Cloning repository..."
if [ ! -d "$APP_DIR/.git" ]; then
    sudo -u $USER git clone https://github.com/your-org/skinguard.git $APP_DIR
else
    print_warning "Repository already cloned"
    cd $APP_DIR
    sudo -u $USER git pull
fi

# Set up Python virtual environment
print_status "Setting up Python virtual environment..."
cd $APP_DIR
sudo -u $USER python3 -m venv venv
sudo -u $USER ./venv/bin/pip install --upgrade pip
sudo -u $USER ./venv/bin/pip install -r backend/requirements.txt
sudo -u $USER ./venv/bin/pip install gunicorn

# Download AI models
print_status "Downloading AI models..."
if [ ! -f "$MODELS_DIR/models_downloaded" ]; then
    sudo -u $USER ./venv/bin/python scripts/download_models.py --output $MODELS_DIR
    touch $MODELS_DIR/models_downloaded
    print_status "AI models downloaded"
else
    print_warning "AI models already downloaded"
fi

# Set up environment variables
print_status "Setting up environment variables..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/deployment/.env.production.example $APP_DIR/.env
    print_warning "Please edit $APP_DIR/.env with your production values"
else
    print_warning ".env file already exists"
fi

# Configure Supervisor
print_status "Configuring Supervisor..."
cat > /etc/supervisor/conf.d/skinguard.conf <<EOF
[program:skinguard-backend]
command=$APP_DIR/venv/bin/gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --access-logfile $LOGS_DIR/access.log --error-logfile $LOGS_DIR/error.log
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=$LOGS_DIR/supervisor-error.log
stdout_logfile=$LOGS_DIR/supervisor-output.log
environment=PATH="$APP_DIR/venv/bin"
EOF

# Configure Nginx
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/skinguard <<EOF
server {
    listen 80;
    server_name api.skinguard.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
        
        # File upload
        client_max_body_size 10M;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/skinguard /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Set up SSL with Let's Encrypt
print_status "Setting up SSL certificate..."
apt-get install -y certbot python3-certbot-nginx
print_warning "Run: certbot --nginx -d api.skinguard.com"

# Set up log rotation
print_status "Configuring log rotation..."
cat > /etc/logrotate.d/skinguard <<EOF
$LOGS_DIR/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
    sharedscripts
    postrotate
        supervisorctl restart skinguard-backend > /dev/null 2>&1 || true
    endscript
}
EOF

# Set up firewall
print_status "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Start services
print_status "Starting services..."
supervisorctl reread
supervisorctl update
supervisorctl start skinguard-backend
systemctl restart nginx
systemctl enable supervisor
systemctl enable nginx

# Health check
print_status "Performing health check..."
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend is healthy!"
else
    print_error "Backend health check failed"
    print_warning "Check logs: tail -f $LOGS_DIR/error.log"
fi

# Print summary
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit environment variables: nano $APP_DIR/.env"
echo "2. Set up SSL: certbot --nginx -d api.skinguard.com"
echo "3. Restart backend: supervisorctl restart skinguard-backend"
echo "4. Check logs: tail -f $LOGS_DIR/error.log"
echo "5. Test API: curl http://localhost:8000/health"
echo ""
echo "Useful commands:"
echo "  - View logs: tail -f $LOGS_DIR/error.log"
echo "  - Restart backend: supervisorctl restart skinguard-backend"
echo "  - Check status: supervisorctl status"
echo "  - Update code: cd $APP_DIR && git pull && supervisorctl restart skinguard-backend"
echo ""
