#!/usr/bin/env python3
"""
Example script demonstrating how to use the Customer Purchase Prediction API.
"""

import requests
import json
import time
from typing import Dict, List

# API configuration
API_BASE_URL = "http://localhost:8001"


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error checking API health: {e}")
        return False


def get_model_info():
    """Get information about the loaded model."""
    try:
        response = requests.get(f"{API_BASE_URL}/model_info", timeout=5)
        if response.status_code == 200:
            model_info = response.json()
            print("📊 Model Information:")
            print(f"   Model Type: {model_info.get('model_type', 'Unknown')}")
            print(f"   Feature Count: {model_info.get('feature_count', 0)}")
            print(f"   Model Name: {model_info.get('model_info', {}).get('model_name', 'Unknown')}")
            return model_info
        else:
            print(f"❌ Failed to get model info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting model info: {e}")
        return None


def score_single_customer(customer_id: int, features: Dict) -> Dict:
    """Score a single customer."""
    try:
        payload = {
            "customer_id": customer_id,
            "features": features
        }
        
        response = requests.post(
            f"{API_BASE_URL}/score_customer", 
            json=payload, 
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to score customer: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error scoring customer: {e}")
        return None


def score_multiple_customers(customers: List[Dict]) -> List[Dict]:
    """Score multiple customers in batch."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/score_batch", 
            json=customers, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to score customers: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error scoring customers: {e}")
        return []


def create_sample_customer_features() -> Dict:
    """Create sample customer features for testing."""
    return {
        "recency_days": 15.0,
        "frequency": 25,
        "monetary": 75.50,
        "total_monetary": 1887.50,
        "total_transactions": 25,
        "unique_invoices": 20,
        "unique_products": 18,
        "unique_descriptions": 15,
        "avg_basket_size": 3.2,
        "avg_basket_value": 75.50,
        "spend_30d": 450.0,
        "spend_90d": 1200.0,
        "spend_ratio_30d_90d": 0.375,
        "spend_ratio_90d_180d": 1.2,
        "freq_30d": 2.5,
        "freq_90d": 8.0,
        "transactions_30d": 6,
        "transactions_90d": 18,
        "total_returns": 2,
        "return_rate": 0.08,
        "return_amount": 150.0,
        "net_amount": 1737.50,
        "avg_day_of_week": 3.5,
        "std_day_of_week": 1.8,
        "avg_month": 6.2,
        "std_month": 2.1,
        "weekend_ratio": 0.3,
        "customer_lifetime_days": 180,
        "primary_country": "United Kingdom"
    }


def create_multiple_sample_customers(n_customers: int = 5) -> List[Dict]:
    """Create multiple sample customers for batch testing."""
    import random
    
    customers = []
    for i in range(n_customers):
        customer_id = 1000 + i
        
        # Vary the features slightly for each customer
        base_features = create_sample_customer_features()
        features = {
            key: value * random.uniform(0.8, 1.2) if isinstance(value, float) else value
            for key, value in base_features.items()
        }
        
        # Ensure some values remain integers
        features['frequency'] = int(features['frequency'])
        features['total_transactions'] = int(features['total_transactions'])
        features['unique_invoices'] = int(features['unique_invoices'])
        features['unique_products'] = int(features['unique_products'])
        features['unique_descriptions'] = int(features['unique_descriptions'])
        features['transactions_30d'] = int(features['transactions_30d'])
        features['transactions_90d'] = int(features['transactions_90d'])
        features['total_returns'] = int(features['total_returns'])
        features['customer_lifetime_days'] = int(features['customer_lifetime_days'])
        
        customers.append({
            "customer_id": customer_id,
            "features": features
        })
    
    return customers


def print_customer_score(result: Dict):
    """Print customer score results in a formatted way."""
    if not result:
        print("❌ No result to display")
        return
    
    print(f"\n🎯 Customer {result['customer_id']} Analysis:")
    print("=" * 50)
    print(f"Purchase Probability: {result['purchase_probability']:.1%}")
    print(f"Model Confidence: {result['model_confidence']:.1%}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Timestamp: {result['timestamp']}")
    
    if result['top_features']:
        print(f"\n🔍 Top Influential Features:")
        for i, feature in enumerate(result['top_features'][:5], 1):
            print(f"   {i}. {feature['feature']}: {feature['importance']:.3f}")


def print_batch_results(results: List[Dict]):
    """Print batch scoring results."""
    if not results:
        print("❌ No results to display")
        return
    
    print(f"\n📊 Batch Scoring Results ({len(results)} customers):")
    print("=" * 60)
    
    # Sort by probability
    sorted_results = sorted(results, key=lambda x: x['purchase_probability'], reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        print(f"{i:2d}. Customer {result['customer_id']:4d}: "
              f"{result['purchase_probability']:.1%} ({result['recommendation']})")
    
    # Summary statistics
    probabilities = [r['purchase_probability'] for r in results]
    print(f"\n📈 Summary:")
    print(f"   Average Probability: {sum(probabilities)/len(probabilities):.1%}")
    print(f"   Highest Probability: {max(probabilities):.1%}")
    print(f"   Lowest Probability: {min(probabilities):.1%}")
    
    # Recommendation breakdown
    recommendations = [r['recommendation'] for r in results]
    from collections import Counter
    rec_counts = Counter(recommendations)
    print(f"\n🎯 Recommendations:")
    for rec, count in rec_counts.items():
        print(f"   {rec}: {count} customers")


def main():
    """Main function to demonstrate API usage."""
    print("🚀 Customer Purchase Prediction API Demo")
    print("=" * 50)
    
    # Check API health
    if not check_api_health():
        print("\n💡 To start the API, run:")
        print("   cd src/api")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Get model information
    model_info = get_model_info()
    
    print("\n" + "=" * 50)
    print("📝 Single Customer Scoring Example")
    print("=" * 50)
    
    # Score a single customer
    customer_id = 12345
    features = create_sample_customer_features()
    
    print(f"Scoring customer {customer_id}...")
    result = score_single_customer(customer_id, features)
    
    if result:
        print_customer_score(result)
    else:
        print("❌ Failed to score customer")
    
    print("\n" + "=" * 50)
    print("📊 Batch Customer Scoring Example")
    print("=" * 50)
    
    # Score multiple customers
    customers = create_multiple_sample_customers(10)
    print(f"Scoring {len(customers)} customers in batch...")
    
    start_time = time.time()
    batch_results = score_multiple_customers(customers)
    end_time = time.time()
    
    if batch_results:
        print(f"✅ Batch scoring completed in {end_time - start_time:.2f} seconds")
        print_batch_results(batch_results)
    else:
        print("❌ Failed to score customers in batch")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("=" * 50)
    
    print("\n💡 Additional API endpoints:")
    print("   GET  /health          - Health check")
    print("   GET  /model_info      - Model information")
    print("   GET  /feature_names   - List of feature names")
    print("   POST /score_customer  - Score single customer")
    print("   POST /score_batch     - Score multiple customers")
    
    print("\n📖 API Documentation:")
    print("   http://localhost:8000/docs")


if __name__ == "__main__":
    main()
