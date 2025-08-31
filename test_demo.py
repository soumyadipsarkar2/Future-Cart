#!/usr/bin/env python3
"""
Demo script to test the Customer Purchase Prediction project.
"""

import requests
import json
import time

def test_api_health():
    """Test API health endpoint."""
    print("🔍 Testing API Health...")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_model_info():
    """Test model info endpoint."""
    print("\n🔍 Testing Model Info...")
    try:
        response = requests.get("http://localhost:8001/model_info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info retrieved:")
            print(f"   Model: {data['model_info']['model_name']}")
            print(f"   Features: {data['feature_count']}")
            print(f"   Type: {data['model_type']}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_customer_scoring():
    """Test customer scoring endpoint."""
    print("\n🔍 Testing Customer Scoring...")
    
    # Sample customer features
    customer_data = {
        "customer_id": 12345,
        "features": {
            "recency_days": 15.0,
            "frequency": 5,
            "monetary": 150.0,
            "total_monetary": 750.0,
            "total_transactions": 5,
            "unique_invoices": 5,
            "unique_products": 12,
            "unique_descriptions": 12,
            "avg_basket_size": 2.4,
            "avg_basket_value": 150.0,
            "spend_30d": 300.0,
            "spend_90d": 750.0,
            "spend_ratio_30d_90d": 0.4,
            "spend_ratio_90d_180d": 0.8,
            "freq_30d": 2.0,
            "freq_90d": 5.0,
            "transactions_30d": 2,
            "transactions_90d": 5,
            "total_returns": 0,
            "return_rate": 0.1,
            "return_amount": 75.0,
            "net_amount": 675.0,
            "avg_day_of_week": 3.0,
            "std_day_of_week": 1.5,
            "avg_month": 6.0,
            "std_month": 2.0,
            "weekend_ratio": 0.3,
            "customer_lifetime_days": 180,
            "primary_country": "United Kingdom"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/score_customer",
            headers={"Content-Type": "application/json"},
            data=json.dumps(customer_data)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Customer scoring successful:")
            print(f"   Customer ID: {data['customer_id']}")
            print(f"   Purchase Probability: {data['purchase_probability']:.3f}")
            print(f"   Recommendation: {data['recommendation']}")
            print(f"   Confidence: {data['model_confidence']:.3f}")
            return True
        else:
            print(f"❌ Customer scoring failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Customer scoring error: {e}")
        return False

def test_dashboard():
    """Test dashboard accessibility."""
    print("\n🔍 Testing Dashboard...")
    try:
        response = requests.get("http://localhost:8501")
        if response.status_code == 200:
            print("✅ Dashboard is accessible at http://localhost:8501")
            return True
        else:
            print(f"❌ Dashboard check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard check error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Customer Purchase Prediction Project Demo")
    print("=" * 50)
    
    # Test API health
    api_healthy = test_api_health()
    
    # Test model info
    model_info_ok = test_model_info()
    
    # Test customer scoring
    scoring_ok = test_customer_scoring()
    
    # Test dashboard
    dashboard_ok = test_dashboard()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   API Health: {'✅' if api_healthy else '❌'}")
    print(f"   Model Info: {'✅' if model_info_ok else '❌'}")
    print(f"   Customer Scoring: {'✅' if scoring_ok else '❌'}")
    print(f"   Dashboard: {'✅' if dashboard_ok else '❌'}")
    
    if all([api_healthy, model_info_ok, scoring_ok, dashboard_ok]):
        print("\n🎉 All tests passed! The project is running successfully.")
        print("\n📱 Access points:")
        print("   - API Documentation: http://localhost:8001/docs")
        print("   - Dashboard: http://localhost:8501")
        print("   - API Health: http://localhost:8001/health")
    else:
        print("\n⚠️  Some tests failed. Please check the services.")
    
    print("\n🔧 To stop the services:")
    print("   - Press Ctrl+C in the terminal where uvicorn is running")
    print("   - Press Ctrl+C in the terminal where streamlit is running")

if __name__ == "__main__":
    main()
