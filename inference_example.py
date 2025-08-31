#!/usr/bin/env python3
"""
Example inference script showing how to use the trained models.
This demonstrates the proper way to load and use the trained models
without needing to retrain.
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from utils.feature_engineering import FeatureEngineer

def load_trained_model(model_path: str):
    """Load a trained model from disk."""
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    return model_data

def create_sample_customer_features():
    """Create sample customer features that match the training format."""
    # This would normally come from your feature engineering pipeline
    # For demonstration, we'll create sample features
    
    # Sample customer data (this would be your raw customer data)
    sample_data = pd.DataFrame({
        'CustomerID': [12345],
        'InvoiceDate': ['2011-11-01'],
        'Quantity': [10],
        'UnitPrice': [15.0],
        'Country': ['United Kingdom'],
        'InvoiceNo': ['INV001'],
        'StockCode': ['PROD001'],
        'Description': ['Sample Product']
    })
    
    # Create features using the same feature engineering pipeline
    feature_engineer = FeatureEngineer()
    features = feature_engineer.create_all_features(sample_data)
    
    return features

def predict_customer_purchase(customer_features, model_path="models/random_forest_model.pkl"):
    """Predict purchase probability for a customer."""
    
    # Load the trained model
    model_data = load_trained_model(model_path)
    model = model_data['model']
    
    # Prepare features (remove CustomerID and ensure correct format)
    X = customer_features.drop('CustomerID', axis=1)
    
    # Make prediction
    probability = model.predict_proba(X)[0, 1]  # Probability of positive class
    
    return {
        'customer_id': customer_features['CustomerID'].iloc[0],
        'purchase_probability': probability,
        'recommendation': get_recommendation(probability),
        'model_used': model_data.get('name', 'Unknown')
    }

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

def main():
    """Main function demonstrating model inference."""
    print("🎯 Customer Purchase Prediction - Inference Example")
    print("=" * 60)
    
    # Load available models
    models_dir = Path("models")
    available_models = list(models_dir.glob("*_model.pkl"))
    
    print(f"📁 Found {len(available_models)} trained models:")
    for model_path in available_models:
        print(f"   - {model_path.name}")
    
    print("\n🔍 Loading model details...")
    
    # Load and examine the Random Forest model
    rf_model_path = "models/random_forest_model.pkl"
    if Path(rf_model_path).exists():
        model_data = load_trained_model(rf_model_path)
        print(f"✅ Model loaded: {model_data.get('name', 'Unknown')}")
        print(f"   Model type: {type(model_data['model']).__name__}")
        print(f"   Is fitted: {model_data.get('is_fitted', 'Unknown')}")
    
    print("\n📊 Creating sample customer features...")
    
    try:
        # Create sample features
        customer_features = create_sample_customer_features()
        print(f"✅ Features created: {len(customer_features.columns)} features")
        print(f"   Feature names: {list(customer_features.columns)}")
        
        print("\n🎯 Making prediction...")
        
        # Make prediction
        result = predict_customer_purchase(customer_features, rf_model_path)
        
        print(f"✅ Prediction successful!")
        print(f"   Customer ID: {result['customer_id']}")
        print(f"   Purchase Probability: {result['purchase_probability']:.3f}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Model Used: {result['model_used']}")
        
    except Exception as e:
        print(f"❌ Error during inference: {e}")
        print("\n💡 This demonstrates why proper feature engineering consistency is important!")
        print("   The model expects specific feature names and formats that must match training.")
    
    print("\n" + "=" * 60)
    print("📚 Key Takeaways:")
    print("1. ✅ Models are saved and can be loaded without retraining")
    print("2. ✅ Feature engineering must be consistent between training and inference")
    print("3. ✅ The same preprocessing pipeline should be used")
    print("4. ✅ Model artifacts (.pkl files) contain all necessary information")
    
    print("\n🚀 Next Steps:")
    print("- Use the same feature engineering pipeline for new data")
    print("- Ensure feature names and formats match exactly")
    print("- Deploy the trained models with proper preprocessing")

if __name__ == "__main__":
    main()
