#!/bin/bash

# Railway Deployment Script (Free Alternative to AWS App Runner)
echo "🚂 Deploying to Railway (Free Alternative)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Railway is a free alternative to AWS App Runner with no subscription issues.${NC}"
echo ""

echo -e "${BLUE}📋 Step 1: Install Railway CLI${NC}"
echo "Run this command to install Railway CLI:"
echo "npm install -g @railway/cli"
echo ""

echo -e "${BLUE}📋 Step 2: Login to Railway${NC}"
echo "Run this command to login:"
echo "railway login"
echo ""

echo -e "${BLUE}📋 Step 3: Deploy to Railway${NC}"
echo "Run these commands:"
echo "railway init"
echo "railway up"
echo ""

echo -e "${GREEN}✅ Railway will give you a public URL instantly!${NC}"
echo ""
echo -e "${BLUE}🔗 Railway Website: https://railway.app/${NC}"
echo ""
echo -e "${YELLOW}💡 Benefits of Railway:${NC}"
echo "✅ No subscription required"
echo "✅ Free tier available"
echo "✅ Instant deployment"
echo "✅ Automatic HTTPS"
echo "✅ Easy to use"
echo ""
echo -e "${GREEN}🎉 Your app will be live in minutes!${NC}"
