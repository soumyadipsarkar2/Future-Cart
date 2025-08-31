#!/usr/bin/env python3
"""
Main script to run the complete Customer Purchase Prediction pipeline.
"""

import os
import sys
import logging
import argparse
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from utils.data_loader import DataLoader, load_sample_data
from utils.feature_engineering import FeatureEngineer
from models.base_models import ModelFactory
from models.ensemble_models import EnsembleFactory
from utils.evaluation import ModelEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_data_preprocessing():
    """Run data preprocessing pipeline."""
    logger.info("Starting data preprocessing...")
    
    # Initialize data loader
    data_loader = DataLoader()
    
    # Load and preprocess data
    preprocessed_data = data_loader.basic_preprocessing()
    logger.info(f"Preprocessed data: {len(preprocessed_data)} rows")
    
    # Create labels
    labels = data_loader.create_labels(preprocessed_data)
    logger.info(f"Created labels for {len(labels)} customers")
    
    # Split data
    train_data, test_data = data_loader.get_train_test_split(preprocessed_data)
    train_labels, test_labels = data_loader.get_train_test_split(labels)
    
    logger.info(f"Train set: {len(train_data)} transactions, {len(train_labels)} customers")
    logger.info(f"Test set: {len(test_data)} transactions, {len(test_labels)} customers")
    
    return train_data, test_data, train_labels, test_labels


def run_feature_engineering(train_data, test_data):
    """Run feature engineering pipeline."""
    logger.info("Starting feature engineering...")
    
    # Initialize feature engineer
    feature_engineer = FeatureEngineer()
    
    # Create features for train set
    train_features = feature_engineer.create_all_features(train_data)
    logger.info(f"Created {len(train_features.columns)} features for train set")
    
    # Create features for test set (using train features as reference)
    test_features = feature_engineer.create_all_features(test_data, reference_features=train_features)
    logger.info(f"Created {len(test_features.columns)} features for test set")
    
    return train_features, test_features


def run_model_training(train_features, train_labels):
    """Run model training pipeline."""
    logger.info("Starting model training...")
    
    # Prepare data
    X_train = train_features.drop('CustomerID', axis=1)
    y_train = train_labels['will_purchase']
    
    # Create models
    models = ModelFactory.create_all_models()
    
    # Train models
    trained_models = {}
    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        logger.info(f"Finished training {name}")
    
    return trained_models


def run_ensemble_training(train_features, train_labels):
    """Run ensemble model training."""
    logger.info("Starting ensemble training...")
    
    # Prepare data
    X_train = train_features.drop('CustomerID', axis=1)
    y_train = train_labels['will_purchase']
    
    # Create ensemble models
    stacking_ensemble = EnsembleFactory.create_stacking_ensemble()
    blending_ensemble = EnsembleFactory.create_blending_ensemble()
    
    # Train ensembles
    logger.info("Training stacking ensemble...")
    stacking_ensemble.fit(X_train, y_train)
    
    logger.info("Training blending ensemble...")
    blending_ensemble.fit(X_train, y_train)
    
    return {
        'stacking': stacking_ensemble,
        'blending': blending_ensemble
    }


def run_evaluation(models, ensembles, test_features, test_labels):
    """Run model evaluation."""
    logger.info("Starting model evaluation...")
    
    # Prepare test data
    X_test = test_features.drop('CustomerID', axis=1)
    y_test = test_labels['will_purchase']
    
    results = {}
    
    # Evaluate individual models
    for name, model in models.items():
        logger.info(f"Evaluating {name}...")
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        evaluator = ModelEvaluator(y_test.values, y_pred, y_proba)
        metrics = evaluator.calculate_basic_metrics()
        
        results[name] = metrics
        logger.info(f"{name} - ROC-AUC: {metrics['roc_auc']:.3f}, PR-AUC: {metrics['pr_auc']:.3f}")
    
    # Evaluate ensemble models
    for name, ensemble in ensembles.items():
        logger.info(f"Evaluating {name} ensemble...")
        
        y_pred = ensemble.predict(X_test)
        y_proba = ensemble.predict_proba(X_test)[:, 1]
        
        evaluator = ModelEvaluator(y_test.values, y_pred, y_proba)
        metrics = evaluator.calculate_basic_metrics()
        
        results[f"{name}_ensemble"] = metrics
        logger.info(f"{name} ensemble - ROC-AUC: {metrics['roc_auc']:.3f}, PR-AUC: {metrics['pr_auc']:.3f}")
    
    return results


def save_models(models, ensembles, results):
    """Save trained models and results."""
    logger.info("Saving models and results...")
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save individual models
    for name, model in models.items():
        model_path = f'models/{name}_model.pkl'
        model.save_model(model_path)
        logger.info(f"Saved {name} model to {model_path}")
    
    # Save ensemble models
    for name, ensemble in ensembles.items():
        model_path = f'models/{name}_ensemble.pkl'
        ensemble.save_model(model_path)
        logger.info(f"Saved {name} ensemble to {model_path}")
    
    # Save results
    import json
    with open('models/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    logger.info("Saved results to models/results.json")


def main():
    """Main pipeline function."""
    parser = argparse.ArgumentParser(description='Run Customer Purchase Prediction Pipeline')
    parser.add_argument('--skip-preprocessing', action='store_true', 
                       help='Skip data preprocessing')
    parser.add_argument('--skip-features', action='store_true',
                       help='Skip feature engineering')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training')
    parser.add_argument('--skip-evaluation', action='store_true',
                       help='Skip model evaluation')
    
    args = parser.parse_args()
    
    logger.info("Starting Customer Purchase Prediction Pipeline")
    logger.info("=" * 60)
    
    try:
        # Data preprocessing
        if not args.skip_preprocessing:
            train_data, test_data, train_labels, test_labels = run_data_preprocessing()
        else:
            logger.info("Skipping data preprocessing")
            # Load preprocessed data if available
            try:
                train_data = pd.read_csv('data/processed/train_transactions.csv')
                test_data = pd.read_csv('data/processed/test_transactions.csv')
                train_labels = pd.read_csv('data/processed/train_labels.csv')
                test_labels = pd.read_csv('data/processed/test_labels.csv')
                logger.info("Loaded preprocessed data")
            except FileNotFoundError:
                logger.error("Preprocessed data not found. Please run preprocessing first.")
                return
        
        # Feature engineering
        if not args.skip_features:
            train_features, test_features = run_feature_engineering(train_data, test_data)
        else:
            logger.info("Skipping feature engineering")
            # Load features if available
            try:
                train_features = pd.read_csv('data/processed/train_features.csv')
                test_features = pd.read_csv('data/processed/test_features.csv')
                logger.info("Loaded engineered features")
            except FileNotFoundError:
                logger.error("Engineered features not found. Please run feature engineering first.")
                return
        
        # Model training
        if not args.skip_training:
            models = run_model_training(train_features, train_labels)
            ensembles = run_ensemble_training(train_features, train_labels)
        else:
            logger.info("Skipping model training")
            models = {}
            ensembles = {}
        
        # Model evaluation
        if not args.skip_evaluation and models:
            results = run_evaluation(models, ensembles, test_features, test_labels)
            save_models(models, ensembles, results)
        else:
            logger.info("Skipping model evaluation")
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
