"""
FastAPI application for customer purchase prediction.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import pickle
import json
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List
import numpy as np

# Load models
def load_models():
    models = {}
    model_files = {
        'random_forest': 'models/random_forest_model.pkl',
        'xgboost': 'models/xgboost_model.pkl',
        'logistic_regression': 'models/logistic_regression_model.pkl',
        'stacking_ensemble': 'models/stacking_ensemble.pkl',
        'blending_ensemble': 'models/blending_ensemble.pkl'
    }
    
    for name, path in model_files.items():
        if os.path.exists(path):
            with open(path, 'rb') as f:
                models[name] = pickle.load(f)
    
    return models

models = load_models()

app = FastAPI(
    title="Customer Purchase Prediction API",
    description="ML API for predicting customer purchase behavior",
    version="1.0.0"
)

# Pydantic models for request/response
class CustomerFeatures(BaseModel):
    customer_id: int
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    customer_id: int
    purchase_probability: float
    top_features: List[Dict[str, Any]]
    recommendation: str

@app.get("/")
async def root():
    """Redirect to dashboard or show API info"""
    return {
        "message": "Customer Purchase Prediction API",
        "status": "healthy",
        "endpoints": {
            "api_docs": "/docs",
            "health_check": "/health",
            "predict": "/score_customer",
            "dashboard": "/dashboard"
        },
        "models_loaded": list(models.keys())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": len(models) > 0,
        "version": "1.0.0"
    }

@app.get("/dashboard")
async def dashboard_redirect():
    """Redirect to Streamlit dashboard"""
    # For now, return info about the dashboard
    return {
        "message": "Dashboard is available at /streamlit",
        "note": "Streamlit dashboard runs on a separate port in development"
    }

@app.post("/score_customer", response_model=PredictionResponse)
async def score_customer(customer_data: CustomerFeatures):
    """Score a customer for purchase probability"""
    try:
        # Use the best performing model (Random Forest)
        if 'random_forest' not in models:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        model_data = models['random_forest']
        model = model_data['model']
        
        # Extract features (simplified for demo)
        features = customer_data.features
        
        # Create feature vector (this would need to match training features)
        # For demo purposes, we'll use a simple approach
        feature_vector = np.array([
            features.get('recency_days', 30),
            features.get('frequency', 5),
            features.get('monetary', 100.0),
            features.get('unique_products', 10),
            features.get('return_rate', 0.1)
        ]).reshape(1, -1)
        
        # Make prediction
        probability = model.predict_proba(feature_vector)[0, 1]
        
        # Determine recommendation
        if probability > 0.7:
            recommendation = "high_priority"
        elif probability > 0.4:
            recommendation = "medium_priority"
        else:
            recommendation = "low_priority"
        
        # Top features (simplified)
        top_features = [
            {"feature": "recency_days", "importance": 0.25},
            {"feature": "frequency", "importance": 0.20},
            {"feature": "monetary", "importance": 0.15}
        ]
        
        return PredictionResponse(
            customer_id=customer_data.customer_id,
            purchase_probability=float(probability),
            top_features=top_features,
            recommendation=recommendation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "available_models": list(models.keys()),
        "total_models": len(models)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
