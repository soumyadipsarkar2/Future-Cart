#!/bin/bash

# Fix IAM Permissions for GitHub Actions
echo "🔧 Fixing IAM Permissions for GitHub Actions..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}This script will fix the IAM permissions for your GitHub Actions deployment.${NC}"
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
echo -e "${YELLOW}⚠️  You need to manually update the IAM user permissions in AWS Console.${NC}"
echo ""
echo -e "${BLUE}📋 Follow these steps:${NC}"
echo ""
echo "1. Go to AWS Console: https://console.aws.amazon.com/"
echo "2. Search for 'IAM' in the services"
echo "3. Click 'Users' in the left sidebar"
echo "4. Find and click on user: 'github-actions-deploy'"
echo "5. Click 'Add permissions'"
echo "6. Choose 'Attach policies directly'"
echo "7. Search and select these policies:"
echo "   - AmazonEC2ContainerRegistryFullAccess"
echo "   - AWSAppRunnerFullAccess"
echo "   - IAMFullAccess"
echo "8. Click 'Next' and 'Add permissions'"
echo ""
echo -e "${GREEN}✅ After adding these permissions, your GitHub Actions will work!${NC}"
echo ""
echo -e "${BLUE}🔗 Direct link to IAM Users:${NC}"
echo "https://console.aws.amazon.com/iam/home#/users"
echo ""
echo -e "${YELLOW}💡 Alternative: You can also run this command with your root AWS credentials:${NC}"
echo ""
echo "aws iam attach-user-policy --user-name github-actions-deploy --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
echo "aws iam attach-user-policy --user-name github-actions-deploy --policy-arn arn:aws:iam::aws:policy/AWSAppRunnerFullAccess"
echo "aws iam attach-user-policy --user-name github-actions-deploy --policy-arn arn:aws:iam::aws:policy/IAMFullAccess"
