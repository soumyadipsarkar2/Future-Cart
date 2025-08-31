"""
FastAPI application for customer purchase prediction.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import joblib
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Purchase Prediction API",
    description="API for predicting customer purchase probability using ensemble ML models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CustomerFeatures(BaseModel):
    """Customer features for prediction."""
    recency_days: float = Field(..., description="Days since last purchase")
    frequency: int = Field(..., description="Total number of transactions")
    monetary: float = Field(..., description="Average transaction value")
    total_monetary: float = Field(..., description="Total amount spent")
    total_transactions: int = Field(..., description="Total number of transactions")
    unique_invoices: int = Field(..., description="Number of unique invoices")
    unique_products: int = Field(..., description="Number of unique products purchased")
    unique_descriptions: int = Field(..., description="Number of unique product descriptions")
    avg_basket_size: float = Field(..., description="Average items per basket")
    avg_basket_value: float = Field(..., description="Average basket value")
    spend_30d: float = Field(..., description="Spend in last 30 days")
    spend_90d: float = Field(..., description="Spend in last 90 days")
    spend_ratio_30d_90d: float = Field(..., description="Ratio of 30d to 90d spend")
    spend_ratio_90d_180d: float = Field(..., description="Ratio of 90d to 180d spend")
    freq_30d: float = Field(..., description="Purchase frequency in last 30 days")
    freq_90d: float = Field(..., description="Purchase frequency in last 90 days")
    transactions_30d: int = Field(..., description="Transactions in last 30 days")
    transactions_90d: int = Field(..., description="Transactions in last 90 days")
    total_returns: int = Field(..., description="Total number of returns")
    return_rate: float = Field(..., description="Return rate")
    return_amount: float = Field(..., description="Total return amount")
    net_amount: float = Field(..., description="Net amount after returns")
    avg_day_of_week: float = Field(..., description="Average day of week for purchases")
    std_day_of_week: float = Field(..., description="Standard deviation of purchase day")
    avg_month: float = Field(..., description="Average month for purchases")
    std_month: float = Field(..., description="Standard deviation of purchase month")
    weekend_ratio: float = Field(..., description="Ratio of weekend purchases")
    customer_lifetime_days: int = Field(..., description="Customer lifetime in days")
    primary_country: str = Field(..., description="Primary country of customer")

class CustomerScoreRequest(BaseModel):
    """Request model for customer scoring."""
    customer_id: int = Field(..., description="Customer ID")
    features: CustomerFeatures = Field(..., description="Customer features")

class FeatureImportance(BaseModel):
    """Feature importance model."""
    feature: str = Field(..., description="Feature name")
    importance: float = Field(..., description="Feature importance score")

class CustomerScoreResponse(BaseModel):
    """Response model for customer scoring."""
    customer_id: int = Field(..., description="Customer ID")
    purchase_probability: float = Field(..., description="Probability of purchase in next 30 days")
    top_features: List[FeatureImportance] = Field(..., description="Top important features")
    recommendation: str = Field(..., description="Recommendation category")
    model_confidence: float = Field(..., description="Model confidence score")
    timestamp: str = Field(..., description="Prediction timestamp")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    version: str = Field(..., description="API version")

# Global variables for model
model = None
feature_names = None
model_info = {}

def load_model(model_path: str = "../../models/random_forest_model.pkl"):
    """Load the trained model."""
    global model, feature_names, model_info
    
    try:
        if os.path.exists(model_path):
            # Load our custom model format
            import pickle
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            model = model_data['model']
            # For our models, we need to get feature names from the data
            # We'll use a default set based on our feature engineering
            feature_names = [
                'recency_days', 'frequency', 'monetary', 'total_monetary',
                'total_transactions', 'unique_invoices', 'unique_products',
                'unique_descriptions', 'avg_basket_size', 'avg_basket_value',
                'spend_30d', 'spend_90d', 'spend_ratio_30d_90d', 'spend_ratio_90d_180d',
                'freq_30d', 'freq_90d', 'transactions_30d', 'transactions_90d',
                'total_returns', 'return_rate', 'return_amount', 'net_amount',
                'avg_day_of_week', 'std_day_of_week', 'avg_month', 'std_month',
                'weekend_ratio', 'customer_lifetime_days', 'primary_country'
            ]
            model_info = {
                'model_name': model_data.get('name', 'RandomForest'),
                'training_date': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            logger.info(f"Model loaded successfully: {model_info}")
        else:
            logger.warning(f"Model file not found: {model_path}")
            # Load a dummy model for testing
            load_dummy_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        load_dummy_model()

def load_dummy_model():
    """Load a dummy model for testing purposes."""
    global model, feature_names, model_info
    
    from sklearn.ensemble import RandomForestClassifier
    
    # Create a dummy model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    # Create dummy data and fit
    X_dummy = np.random.rand(100, 20)
    y_dummy = np.random.randint(0, 2, 100)
    model.fit(X_dummy, y_dummy)
    
    feature_names = [
        'recency_days', 'frequency', 'monetary', 'total_monetary',
        'total_transactions', 'unique_invoices', 'unique_products',
        'unique_descriptions', 'avg_basket_size', 'avg_basket_value',
        'spend_30d', 'spend_90d', 'spend_ratio_30d_90d', 'spend_ratio_90d_180d',
        'freq_30d', 'freq_90d', 'transactions_30d', 'transactions_90d',
        'total_returns', 'return_rate', 'return_amount', 'net_amount'
    ]
    
    model_info = {
        'model_name': 'DummyModel',
        'training_date': datetime.now().isoformat(),
        'version': '1.0.0'
    }
    
    logger.info("Dummy model loaded for testing")

def get_feature_importance(model, feature_names: List[str], X: pd.DataFrame) -> List[FeatureImportance]:
    """Get feature importance for the prediction."""
    try:
        if hasattr(model, 'feature_importances_'):
            # For tree-based models
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # For linear models
            importances = np.abs(model.coef_[0])
        else:
            # Default: equal importance
            importances = np.ones(len(feature_names)) / len(feature_names)
        
        # Create feature importance list
        feature_importance_list = []
        for feature, importance in zip(feature_names, importances):
            feature_importance_list.append(FeatureImportance(
                feature=feature,
                importance=float(importance)
            ))
        
        # Sort by importance and return top 10
        feature_importance_list.sort(key=lambda x: x.importance, reverse=True)
        return feature_importance_list[:10]
        
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        return []

def get_recommendation(probability: float) -> str:
    """Get recommendation based on purchase probability."""
    if probability >= 0.8:
        return "high_priority"
    elif probability >= 0.6:
        return "medium_priority"
    elif probability >= 0.4:
        return "low_priority"
    else:
        return "no_action"

def get_model_confidence(probability: float) -> float:
    """Calculate model confidence based on probability."""
    # Simple confidence calculation: higher confidence for extreme probabilities
    return abs(probability - 0.5) * 2

@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    load_model()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=model is not None,
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=model is not None,
        version="1.0.0"
    )

@app.post("/score_customer", response_model=CustomerScoreResponse)
async def score_customer(request: CustomerScoreRequest):
    """
    Score a customer for purchase probability.
    
    Args:
        request: Customer scoring request with features
        
    Returns:
        Customer score response with probability and recommendations
    """
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Convert features to DataFrame
        feature_dict = request.features.dict()
        
        # Handle country encoding
        country = feature_dict.pop('primary_country')
        country_features = {}
        for country_name in ['United Kingdom', 'Germany', 'France', 'EIRE', 'Spain', 'Netherlands']:
            country_features[f'country_{country_name}'] = 1.0 if country == country_name else 0.0
        
        # Create feature vector
        features = []
        for feature_name in feature_names:
            if feature_name in feature_dict:
                features.append(feature_dict[feature_name])
            elif feature_name in country_features:
                features.append(country_features[feature_name])
            else:
                features.append(0.0)  # Default value for missing features
        
        # Create DataFrame
        X = pd.DataFrame([features], columns=feature_names)
        
        # Make prediction
        probability = model.predict_proba(X)[0, 1]
        
        # Get feature importance
        top_features = get_feature_importance(model, feature_names, X)
        
        # Get recommendation
        recommendation = get_recommendation(probability)
        
        # Calculate confidence
        confidence = get_model_confidence(probability)
        
        return CustomerScoreResponse(
            customer_id=request.customer_id,
            purchase_probability=float(probability),
            top_features=top_features,
            recommendation=recommendation,
            model_confidence=float(confidence),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error scoring customer: {e}")
        raise HTTPException(status_code=500, detail=f"Error scoring customer: {str(e)}")

@app.post("/score_batch")
async def score_batch(customers: List[CustomerScoreRequest]):
    """
    Score multiple customers in batch.
    
    Args:
        customers: List of customer scoring requests
        
    Returns:
        List of customer score responses
    """
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        results = []
        for customer_request in customers:
            # Reuse the single customer scoring logic
            single_result = await score_customer(customer_request)
            results.append(single_result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Error in batch scoring: {str(e)}")

@app.get("/model_info")
async def get_model_info():
    """Get information about the loaded model."""
    return {
        "model_info": model_info,
        "feature_count": len(feature_names) if feature_names else 0,
        "feature_names": feature_names if feature_names else [],
        "model_type": type(model).__name__ if model else None
    }

@app.get("/feature_names")
async def get_feature_names():
    """Get list of feature names used by the model."""
    return {
        "feature_names": feature_names if feature_names else [],
        "feature_count": len(feature_names) if feature_names else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
