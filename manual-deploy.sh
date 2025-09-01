#!/bin/bash

# Manual Deployment Script for AWS App Runner
echo "🚀 Manual AWS App Runner Deployment"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}This script will help you deploy your app manually to AWS App Runner.${NC}"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI configured${NC}"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $AWS_ACCOUNT_ID"

echo ""
echo -e "${BLUE}📋 Step 1: Building and pushing Docker image...${NC}"
echo ""

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build the image
echo "Building Docker image..."
docker build -t customer-purchase-prediction .

# Tag the image
echo "Tagging image..."
docker tag customer-purchase-prediction:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest

# Push to ECR
echo "Pushing to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest

echo ""
echo -e "${GREEN}✅ Docker image pushed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Step 2: Create App Runner Service in AWS Console${NC}"
echo ""
echo -e "${YELLOW}🔗 Go to: https://console.aws.amazon.com/apprunner/${NC}"
echo ""
echo -e "${BLUE}📋 Follow these steps:${NC}"
echo "1. Click 'Create service'"
echo "2. Choose 'Container registry'"
echo "3. Select 'Amazon ECR'"
echo "4. Enter image URI: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest"
echo "5. Click 'Next'"
echo "6. Service name: customer-purchase-prediction"
echo "7. Port: 8000"
echo "8. CPU: 1 vCPU"
echo "9. Memory: 2 GB"
echo "10. Click 'Next'"
echo "11. Access role: AppRunnerECRAccessRole"
echo "12. Click 'Next' and 'Create'"
echo ""
echo -e "${GREEN}🎉 Your app will be live in 2-3 minutes!${NC}"
echo ""
echo -e "${BLUE}📋 Your public URL will be:${NC}"
echo "https://customer-purchase-prediction-xxxxx.us-east-1.awsapprunner.com"
echo ""
echo -e "${BLUE}📚 API Documentation:${NC}"
echo "https://customer-purchase-prediction-xxxxx.us-east-1.awsapprunner.com/docs"
