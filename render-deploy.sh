#!/bin/bash

# Render Deployment Script (Free Alternative)
echo "🎨 Deploying to Render (Free Alternative)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Render is another excellent free alternative to AWS App Runner.${NC}"
echo ""

echo -e "${BLUE}📋 Step 1: Go to Render${NC}"
echo "Visit: https://render.com/"
echo "Sign up for a free account"
echo ""

echo -e "${BLUE}📋 Step 2: Connect Your GitHub Repository${NC}"
echo "1. Click 'New +'"
echo "2. Select 'Web Service'"
echo "3. Connect your GitHub repository: soumyadipsarkar2/Future-Cart"
echo ""

echo -e "${BLUE}📋 Step 3: Configure the Service${NC}"
echo "Name: customer-purchase-prediction"
echo "Environment: Docker"
echo "Branch: main"
echo "Root Directory: ."
echo ""

echo -e "${BLUE}📋 Step 4: Deploy${NC}"
echo "Click 'Create Web Service'"
echo ""

echo -e "${GREEN}✅ Render will give you a public URL instantly!${NC}"
echo ""
echo -e "${BLUE}🔗 Render Website: https://render.com/${NC}"
echo ""
echo -e "${YELLOW}💡 Benefits of Render:${NC}"
echo "✅ No subscription required"
echo "✅ Free tier available"
echo "✅ Automatic deployments"
echo "✅ Custom domains"
echo "✅ Easy GitHub integration"
echo ""
echo -e "${GREEN}🎉 Your app will be live in minutes!${NC}"
