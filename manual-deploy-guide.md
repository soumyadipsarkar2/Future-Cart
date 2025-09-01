# 🖥️ Manual AWS App Runner Deployment Guide

## 🚀 **Deploy Your App Using AWS Console UI**

### **Step 1: Build and Push Docker Image**

First, let's build and push your Docker image to ECR:

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 414987573272.dkr.ecr.us-east-1.amazonaws.com

# Build the image
docker build -t customer-purchase-prediction .

# Tag the image
docker tag customer-purchase-prediction:latest 414987573272.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest

# Push to ECR
docker push 414987573272.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest
```

### **Step 2: Create App Runner Service in AWS Console**

1. **Go to**: https://console.aws.amazon.com/apprunner/
2. **Click "Create service"**
3. **Choose "Container registry"**
4. **Select "Amazon ECR"**
5. **Enter image URI**: `414987573272.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest`
6. **Click "Next"**

### **Step 3: Configure Service**

- **Service name**: `customer-purchase-prediction`
- **Port**: `8000`
- **CPU**: `1 vCPU`
- **Memory**: `2 GB`
- **Click "Next"**

### **Step 4: Configure Access**

- **Access role**: `AppRunnerECRAccessRole`
- **Click "Next"**
- **Review and create**

### **Step 5: Get Your Public URL**

After creation (2-3 minutes), you'll get:
- **Service URL**: `https://customer-purchase-prediction-xxxxx.us-east-1.awsapprunner.com`
- **API Docs**: `/docs`
- **Health Check**: `/health`

## 🎯 **Benefits of Manual Deployment**

✅ **No subscription issues**
✅ **No IAM permission problems**
✅ **Full control over the process**
✅ **Immediate feedback**
✅ **Easy to troubleshoot**

## 🔄 **For Future Updates**

To update your app:

```bash
# Build new image
docker build -t customer-purchase-prediction .

# Tag and push
docker tag customer-purchase-prediction:latest 414987573272.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest
docker push 414987573272.dkr.ecr.us-east-1.amazonaws.com/customer-purchase-prediction:latest

# App Runner will automatically deploy the new image
```

## 💰 **Cost**

- **Free Tier**: 750 hours/month
- **Your Usage**: ~730 hours/month
- **Cost**: $0/month

## 🚀 **Ready to Deploy?**

Run the Docker commands above, then create the App Runner service in the AWS Console!

**Your ML application will be live in minutes!** 🎉
