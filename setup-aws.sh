#!/bin/bash

# AWS Setup Script for Customer Purchase Prediction
# This script helps you set up AWS for free tier deployment

set -e

echo "🚀 AWS Setup Script for Customer Purchase Prediction"
echo "==================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}This script will help you set up AWS for free deployment.${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first:${NC}"
    echo "   brew install awscli"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI found${NC}"

# Check if AWS is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${YELLOW}⚠️ AWS not configured. Let's set it up...${NC}"
    echo ""
    echo "Please enter your AWS credentials:"
    aws configure
else
    echo -e "${GREEN}✅ AWS already configured${NC}"
fi

# Get AWS account ID and region
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=$(aws configure get region || echo "us-east-1")

echo ""
echo -e "${BLUE}📊 AWS Account Information:${NC}"
echo "Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo ""

# Create IAM role for App Runner
echo -e "${BLUE}🔧 Creating App Runner service role...${NC}"

# Create the role
aws iam create-role \
    --role-name AppRunnerECRAccessRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "build.apprunner.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' 2>/dev/null || echo "Role already exists"

# Attach the policy
aws iam attach-role-policy \
    --role-name AppRunnerECRAccessRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess 2>/dev/null || echo "Policy already attached"

echo -e "${GREEN}✅ App Runner service role created${NC}"

# Create ECR repository
echo -e "${BLUE}🐳 Creating ECR repository...${NC}"
aws ecr create-repository --repository-name customer-purchase-prediction --region $AWS_REGION 2>/dev/null || echo "Repository already exists"
echo -e "${GREEN}✅ ECR repository created${NC}"

# Display next steps
echo ""
echo -e "${GREEN}🎉 AWS setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Go to your GitHub repository"
echo "2. Click Settings → Secrets and variables → Actions"
echo "3. Add these secrets:"
echo ""
echo -e "${YELLOW}AWS_ACCESS_KEY_ID=${NC}$(aws configure get aws_access_key_id)"
echo -e "${YELLOW}AWS_SECRET_ACCESS_KEY=${NC}$(aws configure get aws_secret_access_key)"
echo -e "${YELLOW}APPRUNNER_SERVICE_ROLE_ARN=${NC}arn:aws:iam::$AWS_ACCOUNT_ID:role/AppRunnerECRAccessRole"
echo ""
echo "4. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add AWS deployment setup'"
echo "   git push origin main"
echo ""
echo -e "${GREEN}🚀 Your app will be automatically deployed to AWS!${NC}"
