#!/bin/bash
# SkinGuard Backend Deployment Script
# Deploys backend to production environment

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEPLOYMENT_TYPE="${1:-lambda}"  # lambda, ec2, or docker
ENVIRONMENT="${2:-production}"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}SkinGuard Backend Deployment${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo "Deployment Type: $DEPLOYMENT_TYPE"
echo "Environment: $ENVIRONMENT"
echo ""

# Function to print status
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
    
    # Check if .env file exists
    if [ ! -f "deployment/.env.production" ]; then
        print_error ".env.production file not found"
        print_warning "Copy deployment/.env.production.example to deployment/.env.production"
        exit 1
    fi
    
    # Load environment variables
    export $(cat deployment/.env.production | grep -v '^#' | xargs)
    
    print_status "Prerequisites check passed"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    cd tests
    
    # Run unit tests
    echo "Running unit tests..."
    pytest unit/ -v || {
        print_error "Unit tests failed"
        exit 1
    }
    
    # Run property tests
    echo "Running property tests..."
    pytest property/ -v --hypothesis-show-statistics || {
        print_error "Property tests failed"
        exit 1
    }
    
    cd ..
    print_status "All tests passed"
}

# Deploy to AWS Lambda
deploy_lambda() {
    print_status "Deploying to AWS Lambda..."
    
    # Check if serverless is installed
    if ! command -v serverless &> /dev/null; then
        print_error "Serverless Framework not installed"
        print_warning "Install with: npm install -g serverless"
        exit 1
    fi
    
    # Check AWS credentials
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        print_error "AWS credentials not set"
        exit 1
    fi
    
    cd deployment/aws/lambda
    
    # Deploy
    serverless deploy --stage $ENVIRONMENT --verbose
    
    cd ../../..
    print_status "Lambda deployment complete"
}

# Deploy to EC2
deploy_ec2() {
    print_status "Deploying to EC2..."
    
    # Check if SSH key exists
    if [ -z "$EC2_SSH_KEY" ]; then
        print_error "EC2_SSH_KEY not set"
        exit 1
    fi
    
    # Check if EC2 host is set
    if [ -z "$EC2_HOST" ]; then
        print_error "EC2_HOST not set"
        exit 1
    fi
    
    # SSH into EC2 and deploy
    ssh -i "$EC2_SSH_KEY" ubuntu@"$EC2_HOST" << 'ENDSSH'
        set -e
        cd /opt/skinguard
        
        # Pull latest code
        git pull origin main
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Install dependencies
        pip install -r backend/requirements.txt
        
        # Restart service
        sudo supervisorctl restart skinguard-backend
        
        # Check health
        sleep 5
        curl -f http://localhost:8000/health || exit 1
        
        echo "Deployment successful"
ENDSSH
    
    print_status "EC2 deployment complete"
}

# Deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    # Build Docker image
    echo "Building Docker image..."
    docker build -f deployment/docker/Dockerfile.backend -t skinguard/backend:latest .
    
    # Tag for registry
    if [ -n "$DOCKER_REGISTRY" ]; then
        docker tag skinguard/backend:latest $DOCKER_REGISTRY/skinguard/backend:latest
        
        # Push to registry
        echo "Pushing to Docker registry..."
        docker push $DOCKER_REGISTRY/skinguard/backend:latest
    fi
    
    # Deploy with docker-compose
    echo "Starting containers..."
    cd deployment/docker
    docker-compose -f docker-compose.prod.yml up -d backend
    cd ../..
    
    # Wait for container to be healthy
    echo "Waiting for container to be healthy..."
    timeout 60 bash -c 'until docker inspect --format="{{.State.Health.Status}}" skinguard-backend-prod | grep -q "healthy"; do sleep 2; done'
    
    print_status "Docker deployment complete"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    cd database/migrations
    
    for file in *.sql; do
        echo "Running migration: $file"
        psql "$DATABASE_URL" -f "$file" || {
            print_error "Migration $file failed"
            exit 1
        }
    done
    
    cd ../..
    print_status "Migrations complete"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Determine API URL based on deployment type
    case $DEPLOYMENT_TYPE in
        lambda)
            API_URL="https://api.skinguard.com"
            ;;
        ec2)
            API_URL="https://api.skinguard.com"
            ;;
        docker)
            API_URL="http://localhost:8000"
            ;;
    esac
    
    # Check health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)
    
    if [ "$response" -eq 200 ]; then
        print_status "Backend is healthy (HTTP $response)"
    else
        print_error "Health check failed (HTTP $response)"
        exit 1
    fi
}

# Main deployment flow
main() {
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Run tests
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    else
        print_warning "Skipping tests (SKIP_TESTS=true)"
    fi
    
    # Step 3: Run migrations
    if [ "$SKIP_MIGRATIONS" != "true" ]; then
        run_migrations
    else
        print_warning "Skipping migrations (SKIP_MIGRATIONS=true)"
    fi
    
    # Step 4: Deploy based on type
    case $DEPLOYMENT_TYPE in
        lambda)
            deploy_lambda
            ;;
        ec2)
            deploy_ec2
            ;;
        docker)
            deploy_docker
            ;;
        *)
            print_error "Invalid deployment type: $DEPLOYMENT_TYPE"
            echo "Usage: $0 [lambda|ec2|docker] [environment]"
            exit 1
            ;;
    esac
    
    # Step 5: Health check
    health_check
    
    # Success
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "Deployment Type: $DEPLOYMENT_TYPE"
    echo "Environment: $ENVIRONMENT"
    echo "API URL: $API_URL"
    echo ""
    echo "Next steps:"
    echo "1. Monitor logs for errors"
    echo "2. Run smoke tests"
    echo "3. Notify team of deployment"
    echo ""
}

# Run main function
main
