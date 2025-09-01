# ⚡ Quick AWS Deployment (Free Tier)

## 🚀 **Deploy in 5 Minutes - Completely Free!**

### **Step 1: Setup AWS (2 minutes)**
```bash
# Run the setup script
./setup-aws.sh
```

### **Step 2: Add GitHub Secrets (1 minute)**
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `AWS_ACCESS_KEY_ID` (from setup script output)
   - `AWS_SECRET_ACCESS_KEY` (from setup script output)
   - `APPRUNNER_SERVICE_ROLE_ARN` (from setup script output)

### **Step 3: Push to GitHub (1 minute)**
```bash
git add .
git commit -m "Add AWS deployment with CI/CD"
git push origin main
```

### **Step 4: Wait for Deployment (1 minute)**
- GitHub Actions will automatically deploy your app
- You'll get a public URL like: `https://your-app.us-east-1.awsapprunner.com`

## 🆓 **What You Get (Free)**

✅ **24/7 Public URL** - Share with anyone
✅ **Automatic Deployments** - Every push to main
✅ **API Documentation** - Auto-generated at `/docs`
✅ **Health Monitoring** - Built-in health checks
✅ **SSL Certificate** - HTTPS included
✅ **Zero Cost** - Within AWS free tier limits

## 🌐 **Your URLs After Deployment**

- **Main App**: `https://your-app-name.us-east-1.awsapprunner.com`
- **API Docs**: `https://your-app-name.us-east-1.awsapprunner.com/docs`
- **Health Check**: `https://your-app-name.us-east-1.awsapprunner.com/health`

## 🔄 **CI/CD Pipeline**

Every time you push to `main`:
1. ✅ **Tests run** automatically
2. ✅ **Docker image** is built
3. ✅ **Deployed** to AWS App Runner
4. ✅ **Public URL** is updated
5. ✅ **Comment** posted with new URL

## 💰 **Cost: $0/month**

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| App Runner | 750 hours/month | ~730 hours | $0 |
| ECR Storage | 500MB | ~50MB | $0 |
| **Total** | | | **$0** |

## 🎯 **Ready to Deploy?**

Just run:
```bash
./setup-aws.sh
```

Then follow the on-screen instructions!

**Your ML application will be live on the internet in minutes!** 🎉
