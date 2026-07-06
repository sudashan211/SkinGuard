# SkinGuard Production Deployment Configuration

This directory contains all production deployment configurations and infrastructure-as-code files for the SkinGuard AI Skin Cancer Screening Platform.

## Directory Structure

```
deployment/
├── README.md                          # This file
├── docker/                            # Docker configurations
│   ├── Dockerfile.backend            # Backend API container
│   ├── Dockerfile.frontend           # Frontend container
│   └── docker-compose.prod.yml       # Production compose file
├── aws/                               # AWS deployment configs
│   ├── lambda/                       # Lambda function configs
│   ├── ec2/                          # EC2 deployment scripts
│   └── cloudfront/                   # CDN configuration
├── vercel/                            # Vercel frontend deployment
│   └── vercel.json                   # Vercel configuration
├── netlify/                           # Netlify frontend deployment
│   └── netlify.toml                  # Netlify configuration
├── supabase/                          # Supabase production config
│   ├── config.toml                   # Supabase configuration
│   └── migrations/                   # Production migrations
├── ci-cd/                             # CI/CD pipeline configs
│   ├── github-actions.yml            # GitHub Actions workflow
│   ├── gitlab-ci.yml                 # GitLab CI configuration
│   └── jenkins/                      # Jenkins pipeline
├── kubernetes/                        # Kubernetes configs (optional)
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   └── ingress.yaml
├── terraform/                         # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── scripts/                           # Deployment scripts
│   ├── deploy-backend.sh
│   ├── deploy-frontend.sh
│   ├── setup-database.sh
│   └── health-check.sh
└── monitoring/                        # Monitoring configs
    ├── prometheus.yml
    ├── grafana-dashboard.json
    └── alerts.yml
```

## Quick Start

### 1. Backend Deployment (AWS Lambda)

```bash
cd deployment/aws/lambda
./deploy.sh
```

### 2. Backend Deployment (EC2)

```bash
cd deployment/aws/ec2
./setup-ec2.sh
```

### 3. Frontend Deployment (Vercel)

```bash
cd deployment/vercel
vercel --prod
```

### 4. Frontend Deployment (Netlify)

```bash
cd deployment/netlify
netlify deploy --prod
```

### 5. Database Setup (Supabase)

```bash
cd deployment/supabase
supabase db push
```

## Environment Variables

All deployment configurations require environment variables. Copy the example files:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` with your production values.

## Deployment Checklist

- [ ] Configure production environment variables
- [ ] Set up Supabase production instance
- [ ] Deploy backend API (Lambda or EC2)
- [ ] Deploy frontend (Vercel or Netlify)
- [ ] Configure CloudFront CDN for images
- [ ] Set up monitoring and alerting
- [ ] Configure CI/CD pipeline
- [ ] Run smoke tests
- [ ] Enable SSL/TLS certificates
- [ ] Configure domain DNS

## Support

For deployment issues, refer to:
- Main deployment guide: `../DEPLOYMENT_GUIDE.md`
- Backend setup: `../GETTING_STARTED_BACKEND.md`
- Frontend setup: `../frontend/README.md`
