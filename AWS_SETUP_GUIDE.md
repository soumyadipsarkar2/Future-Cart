# 🚀 AWS Free Tier Deployment Guide

## 🆓 **Free AWS Services We'll Use**

1. **AWS App Runner** - Free tier: 750 hours/month (enough for 24/7 deployment)
2. **Amazon ECR** - Free tier: 500MB storage, 500MB/month data transfer
3. **GitHub Actions** - Free tier: 2,000 minutes/month

## 📋 **Step-by-Step Setup**

### **Step 1: Create AWS Account (Free Tier)**

1. Go to [AWS Free Tier](https://aws.amazon.com/free/)
2. Click "Create an AWS Account"
3. Fill in your details
4. **Important**: Use a credit card for verification (you won't be charged within free tier limits)

### **Step 2: Create IAM User for GitHub Actions**

1. Go to AWS Console → IAM
2. Click "Users" → "Create user"
3. Name: `github-actions-deploy`
4. Select "Programmatic access"
5. Attach policies:
   - `AmazonECR-FullAccess`
   - `AWSAppRunnerFullAccess`
   - `IAMFullAccess` (for creating service roles)

### **Step 3: Create App Runner Service Role**

Run this AWS CLI command:

```bash
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
  }'

aws iam attach-role-policy \
  --role-name AppRunnerECRAccessRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
```

### **Step 4: Get Your AWS Credentials**

1. Go to IAM → Users → `github-actions-deploy`
2. Click "Security credentials" tab
3. Create access key
4. Save the **Access Key ID** and **Secret Access Key**

### **Step 5: Set Up GitHub Repository Secrets**

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Add these secrets:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
APPRUNNER_SERVICE_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/AppRunnerECRAccessRole
```

### **Step 6: Push to GitHub**

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit with AWS deployment setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## 🎯 **What Happens Next**

1. **GitHub Actions** automatically triggers on push to main
2. **Tests** run to ensure code quality
3. **Docker image** is built and pushed to ECR
4. **AWS App Runner** deploys your application
5. **Public URL** is generated and commented on your PR

## 🌐 **Your Public URLs**

After deployment, you'll get:
- **Main App**: `https://your-app-name.us-east-1.awsapprunner.com`
- **API Docs**: `https://your-app-name.us-east-1.awsapprunner.com/docs`
- **Health Check**: `https://your-app-name.us-east-1.awsapprunner.com/health`

## 💰 **Cost Breakdown (Free Tier)**

| Service | Free Tier Limit | Your Usage | Cost |
|---------|----------------|------------|------|
| App Runner | 750 hours/month | ~730 hours/month | $0 |
| ECR Storage | 500MB | ~50MB | $0 |
| ECR Transfer | 500MB/month | ~100MB/month | $0 |
| **Total** | | | **$0/month** |

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Access Denied" errors**
   - Check IAM permissions
   - Verify AWS credentials in GitHub secrets

2. **"Repository not found"**
   - Ensure ECR repository exists
   - Check region settings

3. **"Service role not found"**
   - Create the AppRunnerECRAccessRole
   - Verify the ARN in GitHub secrets

### **Useful Commands:**

```bash
# Check App Runner services
aws apprunner list-services --region us-east-1

# Check ECR repositories
aws ecr describe-repositories --region us-east-1

# Get service URL
aws apprunner describe-service --service-arn YOUR_SERVICE_ARN --region us-east-1
```

## 🚀 **Quick Start Commands**

```bash
# 1. Setup AWS CLI
aws configure

# 2. Create service role
./aws-deploy.sh setup

# 3. Deploy manually (optional)
./aws-deploy.sh elastic-beanstalk

# 4. Check status
./aws-deploy.sh status
```

## 📞 **Support**

If you encounter issues:
1. Check GitHub Actions logs
2. Verify AWS credentials
3. Ensure all secrets are set correctly
4. Check AWS Console for service status

**Your application will be automatically deployed every time you push to main!** 🎉
