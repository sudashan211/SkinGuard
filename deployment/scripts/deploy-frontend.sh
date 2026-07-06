#!/bin/bash
# SkinGuard Frontend Deployment Script
# Deploys frontend to Vercel or Netlify

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEPLOYMENT_TARGET="${1:-vercel}"  # vercel or netlify
ENVIRONMENT="${2:-production}"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}SkinGuard Frontend Deployment${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo "Target: $DEPLOYMENT_TARGET"
echo "Environment: $ENVIRONMENT"
echo ""

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm not installed"
        exit 1
    fi
    
    # Load environment variables
    if [ -f "deployment/.env.production" ]; then
        export $(cat deployment/.env.production | grep -v '^#' | grep '^VITE_' | xargs)
    else
        print_warning ".env.production not found, using environment variables"
    fi
    
    print_status "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    cd frontend
    npm ci
    cd ..
    
    print_status "Dependencies installed"
}

# Run linter
run_linter() {
    print_status "Running linter..."
    
    cd frontend
    npm run lint || {
        print_error "Linting failed"
        exit 1
    }
    cd ..
    
    print_status "Linting passed"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    cd frontend
    npm run test || {
        print_error "Tests failed"
        exit 1
    }
    cd ..
    
    print_status "Tests passed"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    
    cd frontend
    npm run build || {
        print_error "Build failed"
        exit 1
    }
    cd ..
    
    print_status "Build complete"
}

# Deploy to Vercel
deploy_vercel() {
    print_status "Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not installed, installing..."
        npm install -g vercel
    fi
    
    # Check Vercel token
    if [ -z "$VERCEL_TOKEN" ]; then
        print_error "VERCEL_TOKEN not set"
        exit 1
    fi
    
    cd frontend
    
    # Deploy
    if [ "$ENVIRONMENT" = "production" ]; then
        vercel --prod --token "$VERCEL_TOKEN" --yes
    else
        vercel --token "$VERCEL_TOKEN" --yes
    fi
    
    cd ..
    print_status "Vercel deployment complete"
}

# Deploy to Netlify
deploy_netlify() {
    print_status "Deploying to Netlify..."
    
    # Check if Netlify CLI is installed
    if ! command -v netlify &> /dev/null; then
        print_warning "Netlify CLI not installed, installing..."
        npm install -g netlify-cli
    fi
    
    # Check Netlify token
    if [ -z "$NETLIFY_AUTH_TOKEN" ]; then
        print_error "NETLIFY_AUTH_TOKEN not set"
        exit 1
    fi
    
    cd frontend
    
    # Deploy
    if [ "$ENVIRONMENT" = "production" ]; then
        netlify deploy --prod --dir=dist --auth="$NETLIFY_AUTH_TOKEN"
    else
        netlify deploy --dir=dist --auth="$NETLIFY_AUTH_TOKEN"
    fi
    
    cd ..
    print_status "Netlify deployment complete"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Determine URL based on target
    case $DEPLOYMENT_TARGET in
        vercel)
            URL="https://skinguard.com"
            ;;
        netlify)
            URL="https://skinguard.netlify.app"
            ;;
    esac
    
    # Wait a bit for deployment to propagate
    sleep 10
    
    # Check if site is accessible
    response=$(curl -s -o /dev/null -w "%{http_code}" $URL)
    
    if [ "$response" -eq 200 ]; then
        print_status "Frontend is accessible (HTTP $response)"
    else
        print_warning "Health check returned HTTP $response (may take time to propagate)"
    fi
}

# Main deployment flow
main() {
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Install dependencies
    install_dependencies
    
    # Step 3: Run linter
    if [ "$SKIP_LINT" != "true" ]; then
        run_linter
    else
        print_warning "Skipping linter (SKIP_LINT=true)"
    fi
    
    # Step 4: Run tests
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    else
        print_warning "Skipping tests (SKIP_TESTS=true)"
    fi
    
    # Step 5: Build
    build_frontend
    
    # Step 6: Deploy
    case $DEPLOYMENT_TARGET in
        vercel)
            deploy_vercel
            ;;
        netlify)
            deploy_netlify
            ;;
        *)
            print_error "Invalid deployment target: $DEPLOYMENT_TARGET"
            echo "Usage: $0 [vercel|netlify] [environment]"
            exit 1
            ;;
    esac
    
    # Step 7: Health check
    health_check
    
    # Success
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "Target: $DEPLOYMENT_TARGET"
    echo "Environment: $ENVIRONMENT"
    echo ""
    echo "Next steps:"
    echo "1. Test the deployed site"
    echo "2. Monitor for errors"
    echo "3. Notify team of deployment"
    echo ""
}

# Run main function
main
