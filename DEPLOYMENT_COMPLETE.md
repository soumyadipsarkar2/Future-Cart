# 🚀 Complete Deployment Guide - Customer Purchase Prediction

## 📋 **Project Overview**

This is a complete ML application that predicts customer purchase probability using ensemble machine learning models. The application includes:

- **Trained ML Models**: 5 models ready for inference (~7.5MB total)
- **FastAPI Backend**: RESTful API for predictions
- **Streamlit Dashboard**: Interactive web interface
- **Production Ready**: Docker containerization and deployment scripts

## 🎯 **Quick Start (5 minutes)**

### **Option 1: Using the Deployment Script (Recommended)**

```bash
# Make script executable
chmod +x deploy.sh

# Deploy everything locally
./deploy.sh local

# Or deploy with Docker
./deploy.sh docker

# Check status
./deploy.sh status

# Stop services
./deploy.sh stop
```

### **Option 2: Manual Deployment**

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Start API
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Start Dashboard (in another terminal)
cd src/dashboard
streamlit run app.py --server.port 8501
```

## 🌐 **Access Your Application**

Once deployed, access your services at:

- **API Service**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc
- **Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## 🐳 **Docker Deployment**

### **Build and Run**

```bash
# Build the Docker image
docker build -t customer-purchase-prediction .

# Run the container
docker run -p 8000:8000 -p 8501:8501 customer-purchase-prediction

# Run in background
docker run -d -p 8000:8000 -p 8501:8501 --name customer-prediction-app customer-purchase-prediction

# View logs
docker logs customer-prediction-app

# Stop container
docker stop customer-prediction-app
```

### **Docker Compose (Alternative)**

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  customer-prediction:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./models:/app/models
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## ☁️ **Cloud Deployment**

### **AWS EC2**

```bash
# 1. Launch EC2 instance (Ubuntu 20.04)
# 2. Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv git docker.io

# 4. Clone and deploy
git clone <your-repo-url>
cd Future-Cart
./deploy.sh docker

# 5. Configure security groups to allow ports 8000 and 8501
```

### **Google Cloud Run**

```bash
# 1. Build and push to Google Container Registry
docker build -t gcr.io/YOUR_PROJECT/customer-prediction .
docker push gcr.io/YOUR_PROJECT/customer-prediction

# 2. Deploy to Cloud Run
gcloud run deploy customer-prediction \
  --image gcr.io/YOUR_PROJECT/customer-prediction \
  --platform managed \
  --allow-unauthenticated \
  --port 8000
```

### **Heroku**

Create `Procfile`:
```
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
```

## 🔧 **API Usage Examples**

### **Single Customer Prediction**

```bash
curl -X POST "http://localhost:8000/score_customer" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": 12345,
       "features": {
         "recency_days": 15,
         "frequency": 5,
         "monetary": 150.0,
         "total_monetary": 750.0,
         "total_transactions": 5,
         "unique_invoices": 5,
         "unique_products": 12,
         "unique_descriptions": 10,
         "avg_basket_size": 2.4,
         "avg_basket_value": 150.0,
         "spend_30d": 300.0,
         "spend_90d": 750.0,
         "spend_ratio_30d_90d": 0.4,
         "spend_ratio_90d_180d": 0.6,
         "freq_30d": 2.0,
         "freq_90d": 5.0,
         "transactions_30d": 2,
         "transactions_90d": 5,
         "total_returns": 1,
         "return_rate": 0.2,
         "return_amount": 30.0,
         "net_amount": 720.0,
         "avg_day_of_week": 3.5,
         "std_day_of_week": 1.5,
         "avg_month": 6.0,
         "std_month": 2.0,
         "weekend_ratio": 0.3,
         "customer_lifetime_days": 180,
         "primary_country": "United Kingdom"
       }
     }'
```

### **Batch Prediction**

```bash
curl -X POST "http://localhost:8000/score_batch" \
     -H "Content-Type: application/json" \
     -d '{
       "customers": [
         {
           "customer_id": 12345,
           "features": { ... }
         },
         {
           "customer_id": 67890,
           "features": { ... }
         }
       ]
     }'
```

### **Model Information**

```bash
curl http://localhost:8000/model_info
```

## 📊 **Dashboard Features**

The Streamlit dashboard provides:

- **Customer Scoring**: Interactive prediction interface
- **Model Performance**: Real-time metrics and visualizations
- **Batch Processing**: Upload CSV files for bulk predictions
- **Feature Analysis**: SHAP explanations and importance
- **ROI Simulation**: Business impact calculations

## 🔒 **Security Considerations**

### **Production Security**

1. **Environment Variables**
```bash
export API_KEY=your-secret-key
export DATABASE_URL=your-db-url
export REDIS_URL=your-redis-url
```

2. **HTTPS/SSL**
```bash
# Use reverse proxy (nginx) with SSL certificates
# Or deploy behind a load balancer with SSL termination
```

3. **Authentication**
```python
# Add authentication middleware to FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Implement your token verification logic
    pass
```

4. **Rate Limiting**
```python
# Add rate limiting middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## 📈 **Monitoring and Logging**

### **Health Checks**

```bash
# Check API health
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/model_info
```

### **Logging**

The application includes comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### **Metrics**

Monitor key metrics:
- API response times
- Prediction accuracy
- Model performance
- Error rates
- Resource usage

## 🔄 **Model Updates**

### **Retraining Pipeline**

```bash
# 1. Add new data to data/raw/
# 2. Run training pipeline
python run_pipeline.py

# 3. Models are automatically updated in models/
# 4. Restart services to use new models
./deploy.sh stop
./deploy.sh docker
```

### **A/B Testing**

```python
# Implement model versioning
models = {
    'v1': load_model('models/random_forest_model.pkl'),
    'v2': load_model('models/xgboost_model.pkl')
}

# Route traffic between models
def get_model_version(customer_id):
    return 'v1' if customer_id % 2 == 0 else 'v2'
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000
lsof -i :8501

# Kill processes
pkill -f uvicorn
pkill -f streamlit
```

2. **Model Loading Errors**
```bash
# Check if models exist
ls -la models/

# Verify model files are not corrupted
python -c "import pickle; pickle.load(open('models/random_forest_model.pkl', 'rb'))"
```

3. **Docker Issues**
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Rebuild image
docker build --no-cache -t customer-purchase-prediction .
```

4. **Memory Issues**
```bash
# Monitor memory usage
htop
docker stats

# Increase Docker memory limit
docker run -m 4g -p 8000:8000 -p 8501:8501 customer-purchase-prediction
```

### **Performance Optimization**

1. **API Optimization**
```python
# Use async endpoints
@app.post("/score_customer_async")
async def score_customer_async(request: CustomerScoreRequest):
    # Async processing
    pass
```

2. **Caching**
```python
# Add Redis caching
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache predictions
cache_key = f"prediction:{customer_id}"
cached_result = redis_client.get(cache_key)
```

3. **Load Balancing**
```bash
# Use multiple instances behind a load balancer
docker run -d -p 8001:8000 customer-purchase-prediction
docker run -d -p 8002:8000 customer-purchase-prediction
docker run -d -p 8003:8000 customer-purchase-prediction
```

## 📞 **Support**

For deployment issues:

1. Check the logs: `docker logs customer-prediction-app`
2. Verify health endpoint: `curl http://localhost:8000/health`
3. Check service status: `./deploy.sh status`
4. Review this deployment guide
5. Check the project documentation

## 🎉 **Success!**

Your Customer Purchase Prediction application is now deployed and ready to use! The trained models are loaded and providing predictions through both the API and dashboard interfaces.

**Next Steps:**
- Test the API endpoints
- Explore the dashboard features
- Integrate with your existing systems
- Monitor performance and usage
- Consider scaling for production loads

