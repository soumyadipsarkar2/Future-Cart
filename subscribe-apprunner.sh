#!/bin/bash

# Subscribe to AWS App Runner Service
echo "🚀 Subscribing to AWS App Runner Service..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}This script will help you subscribe to AWS App Runner service.${NC}"
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
echo -e "${YELLOW}⚠️  You need to manually subscribe to AWS App Runner in the AWS Console.${NC}"
echo ""
echo -e "${BLUE}📋 Follow these steps:${NC}"
echo ""
echo "1. Go to AWS App Runner Console:"
echo "   https://console.aws.amazon.com/apprunner/"
echo ""
echo "2. Click 'Get started' or 'Subscribe'"
echo ""
echo "3. Follow the prompts to subscribe to the service"
echo ""
echo "4. This is FREE within the free tier limits"
echo ""
echo -e "${GREEN}✅ After subscribing, your GitHub Actions will work!${NC}"
echo ""
echo -e "${BLUE}🔗 Direct link to App Runner:${NC}"
echo "https://console.aws.amazon.com/apprunner/"
echo ""
echo -e "${YELLOW}💡 Alternative: You can also try this command:${NC}"
echo ""
echo "aws apprunner list-services --region us-east-1"
echo ""
echo -e "${BLUE}📝 Note: If you see a subscription error, you need to subscribe first.${NC}"
