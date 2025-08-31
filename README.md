# Customer Purchase Prediction - End-to-End ML Project

## 🎯 Project Overview

This project predicts whether a customer will make a purchase in the next 30 days based on their past transaction history. It uses the UCI Online Retail Dataset and implements supervised learning with ensemble methods.

## 📊 Dataset

- **Source**: UCI Machine Learning Repository
- **File**: Online Retail.xlsx
- **Size**: ~500k transactions from UK e-commerce store
- **Period**: Dec 2010 – Dec 2011

### Data Fields
- `InvoiceNo`: Invoice ID (C prefix = canceled/return)
- `StockCode`: Product code
- `Description`: Product name
- `Quantity`: Number of units (negative = return)
- `InvoiceDate`: Transaction date & time
- `UnitPrice`: Price per unit
- `CustomerID`: Customer unique ID
- `Country`: Country of purchase

## 🏗️ Project Structure

```
Customer Purchase Prediction/
├── data/                   # Data files
├── notebooks/              # Jupyter notebooks
│   ├── 01_preprocessing.ipynb
│   ├── 02_features.ipynb
│   ├── 03_models.ipynb
│   ├── 04_ensemble.ipynb
│   └── 05_evaluation.ipynb
├── src/                    # Source code
│   ├── api/               # FastAPI service
│   ├── dashboard/         # Streamlit dashboard
│   ├── models/            # ML models
│   └── utils/             # Utility functions
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── Dockerfile            # Container configuration
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd "Customer Purchase Prediction"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Dataset

Download the Online Retail.xlsx file from [UCI ML Repository](https://archive.ics.uci.edu/dataset/352/online+retail) and place it in the `data/` directory.

### 3. Run the Pipeline

```bash
# Run notebooks in order
jupyter notebook notebooks/01_preprocessing.ipynb
jupyter notebook notebooks/02_features.ipynb
jupyter notebook notebooks/03_models.ipynb
jupyter notebook notebooks/04_ensemble.ipynb
jupyter notebook notebooks/05_evaluation.ipynb
```

### 4. Start API Service

```bash
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Launch Dashboard

```bash
cd src/dashboard
streamlit run app.py
```

## 📈 Features

### Data Preprocessing
- Handle missing CustomerID values
- Remove negative/zero quantities (except returns)
- Create cutoff date for prediction window
- Build binary labels (purchase within 30 days)

### Feature Engineering
- **RFM Features**: Recency, Frequency, Monetary
- **Basket Diversity**: Unique products, categories
- **Momentum Features**: 30d/90d spend ratio, purchase frequency
- **Return Rate**: Customer return behavior
- **Geographic**: Country one-hot encoding

### Models
- **Supervised**: Logistic Regression, Random Forest, XGBoost
- **Ensemble**: Stacking and Blending
- **Class Imbalance**: SMOTE and class weights

### Evaluation
- **Metrics**: PR-AUC, ROC-AUC, Precision@k, Recall@k
- **Business**: Expected net profit, Lift curves
- **Explainability**: SHAP feature importance, Calibration curves

## 🔧 API Usage

### Score Customer Endpoint

```bash
curl -X POST "http://localhost:8000/score_customer" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": 12345,
       "features": {
         "recency_days": 15,
         "frequency": 5,
         "monetary": 150.0,
         "unique_products": 12,
         "return_rate": 0.1,
         "country": "United Kingdom"
       }
     }'
```

Response:
```json
{
  "customer_id": 12345,
  "purchase_probability": 0.75,
  "top_features": [
    {"feature": "recency_days", "importance": 0.25},
    {"feature": "frequency", "importance": 0.20}
  ],
  "recommendation": "high_priority"
}
```

## 📊 Dashboard Features

- **Customer Ranking**: Top N customers by purchase probability
- **SHAP Plots**: Feature importance visualization
- **ROI Simulation**: Expected profit from targeting
- **Model Performance**: Real-time metrics

## 🐳 Docker Deployment

```bash
# Build image
docker build -t customer-purchase-prediction .

# Run container
docker run -p 8000:8000 -p 8501:8501 customer-purchase-prediction
```

## 📝 MLflow Integration

Track experiments and model versions:

```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# View experiments
open http://localhost:5000
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 📊 Business Impact

- **Targeted Marketing**: Focus on high-probability customers
- **Resource Optimization**: Reduce marketing costs
- **Revenue Increase**: Higher conversion rates
- **Customer Retention**: Identify at-risk customers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the development team.
