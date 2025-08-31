#!/usr/bin/env python3
"""
Test script to verify that all components are working correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from utils.data_loader import DataLoader, load_sample_data
        print("✅ DataLoader imported successfully")
    except Exception as e:
        print(f"❌ DataLoader import failed: {e}")
        return False
    
    try:
        from utils.feature_engineering import FeatureEngineer
        print("✅ FeatureEngineer imported successfully")
    except Exception as e:
        print(f"❌ FeatureEngineer import failed: {e}")
        return False
    
    try:
        from models.base_models import ModelFactory
        print("✅ ModelFactory imported successfully")
    except Exception as e:
        print(f"❌ ModelFactory import failed: {e}")
        return False
    
    try:
        from models.ensemble_models import EnsembleFactory
        print("✅ EnsembleFactory imported successfully")
    except Exception as e:
        print(f"❌ EnsembleFactory import failed: {e}")
        return False
    
    try:
        from utils.evaluation import ModelEvaluator
        print("✅ ModelEvaluator imported successfully")
    except Exception as e:
        print(f"❌ ModelEvaluator import failed: {e}")
        return False
    
    try:
        from api.main import app
        print("✅ FastAPI app imported successfully")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    try:
        from dashboard.app import main
        print("✅ Streamlit dashboard imported successfully")
    except Exception as e:
        print(f"❌ Streamlit dashboard import failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test data loading functionality."""
    print("\n📊 Testing data loading...")
    
    try:
        from utils.data_loader import load_sample_data
        data = load_sample_data()
        print(f"✅ Sample data loaded: {len(data)} rows")
        print(f"   Columns: {list(data.columns)}")
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_feature_engineering():
    """Test feature engineering functionality."""
    print("\n🔧 Testing feature engineering...")
    
    try:
        from utils.data_loader import load_sample_data
        from utils.feature_engineering import FeatureEngineer
        
        # Load sample data
        data = load_sample_data()
        
        # Create feature engineer
        feature_engineer = FeatureEngineer()
        
        # Create features
        features = feature_engineer.create_all_features(data)
        print(f"✅ Features created: {len(features)} rows, {len(features.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ Feature engineering failed: {e}")
        return False

def test_model_creation():
    """Test model creation functionality."""
    print("\n🤖 Testing model creation...")
    
    try:
        from models.base_models import ModelFactory
        
        # Create models
        models = ModelFactory.create_all_models()
        print(f"✅ Models created: {list(models.keys())}")
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_ensemble_creation():
    """Test ensemble creation functionality."""
    print("\n🎯 Testing ensemble creation...")
    
    try:
        from models.ensemble_models import EnsembleFactory
        
        # Create ensembles
        stacking = EnsembleFactory.create_stacking_ensemble()
        blending = EnsembleFactory.create_blending_ensemble()
        voting = EnsembleFactory.create_voting_ensemble()
        
        print("✅ Ensembles created: stacking, blending, voting")
        return True
    except Exception as e:
        print(f"❌ Ensemble creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Customer Purchase Prediction - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_loading,
        test_feature_engineering,
        test_model_creation,
        test_ensemble_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The setup is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Download the Online Retail.xlsx dataset")
        print("   2. Place it in the data/ directory")
        print("   3. Run: python run_pipeline.py")
        print("   4. Start API: cd src/api && uvicorn main:app --reload")
        print("   5. Start Dashboard: cd src/dashboard && streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
