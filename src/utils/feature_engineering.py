"""
Feature engineering utilities for customer purchase prediction.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for customer purchase prediction."""
    
    def __init__(self, reference_date: str = "2011-09-01"):
        """
        Initialize FeatureEngineer.
        
        Args:
            reference_date: Reference date for feature calculations
        """
        self.reference_date = pd.to_datetime(reference_date)
        
    def create_rfm_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create RFM (Recency, Frequency, Monetary) features.
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            DataFrame with RFM features per customer
        """
        logger.info("Creating RFM features...")
        
        # Group by customer
        customer_features = df.groupby('CustomerID').agg({
            'InvoiceDate': ['max', 'count'],
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        # Flatten column names
        customer_features.columns = ['CustomerID', 'last_purchase_date', 'total_transactions', 
                                   'total_amount', 'unique_invoices']
        
        # Calculate recency (days since last purchase)
        customer_features['recency_days'] = (
            self.reference_date - customer_features['last_purchase_date']
        ).dt.days
        
        # Calculate frequency (transactions per month)
        customer_features['frequency'] = customer_features['total_transactions']
        
        # Calculate monetary (average amount per transaction)
        customer_features['monetary'] = customer_features['total_amount'] / customer_features['total_transactions']
        
        # Calculate total monetary
        customer_features['total_monetary'] = customer_features['total_amount']
        
        logger.info(f"Created RFM features for {len(customer_features)} customers")
        
        return customer_features[['CustomerID', 'recency_days', 'frequency', 'monetary', 
                                'total_monetary', 'total_transactions', 'unique_invoices']]
    
    def create_basket_diversity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create basket diversity features.
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            DataFrame with basket diversity features per customer
        """
        logger.info("Creating basket diversity features...")
        
        # Unique products per customer
        product_diversity = df.groupby('CustomerID').agg({
            'StockCode': 'nunique',
            'Description': 'nunique'
        }).reset_index()
        product_diversity.columns = ['CustomerID', 'unique_products', 'unique_descriptions']
        
        # Average basket size
        basket_size = df.groupby(['CustomerID', 'InvoiceNo']).agg({
            'StockCode': 'count',
            'TotalAmount': 'sum'
        }).reset_index()
        
        avg_basket = basket_size.groupby('CustomerID').agg({
            'StockCode': 'mean',
            'TotalAmount': 'mean'
        }).reset_index()
        avg_basket.columns = ['CustomerID', 'avg_basket_size', 'avg_basket_value']
        
        # Merge features
        diversity_features = product_diversity.merge(avg_basket, on='CustomerID')
        
        logger.info(f"Created basket diversity features for {len(diversity_features)} customers")
        
        return diversity_features
    
    def create_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create momentum features (30d/90d spend ratio, purchase frequency).
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            DataFrame with momentum features per customer
        """
        logger.info("Creating momentum features...")
        
        # Define time windows
        window_30d = self.reference_date - timedelta(days=30)
        window_90d = self.reference_date - timedelta(days=90)
        window_180d = self.reference_date - timedelta(days=180)
        
        momentum_features = []
        
        for customer_id in df['CustomerID'].unique():
            customer_data = df[df['CustomerID'] == customer_id]
            
            # Recent 30 days
            recent_30d = customer_data[customer_data['InvoiceDate'] >= window_30d]
            spend_30d = recent_30d['TotalAmount'].sum()
            transactions_30d = len(recent_30d)
            
            # Recent 90 days
            recent_90d = customer_data[customer_data['InvoiceDate'] >= window_90d]
            spend_90d = recent_90d['TotalAmount'].sum()
            transactions_90d = len(recent_90d)
            
            # Previous 90 days (90-180 days ago)
            previous_90d = customer_data[
                (customer_data['InvoiceDate'] >= window_180d) & 
                (customer_data['InvoiceDate'] < window_90d)
            ]
            spend_prev_90d = previous_90d['TotalAmount'].sum()
            transactions_prev_90d = len(previous_90d)
            
            # Calculate ratios
            spend_ratio_30d_90d = spend_30d / (spend_90d + 1e-8)
            spend_ratio_90d_180d = spend_90d / (spend_prev_90d + 1e-8)
            
            # Purchase frequency
            freq_30d = transactions_30d / 30
            freq_90d = transactions_90d / 90
            
            momentum_features.append({
                'CustomerID': customer_id,
                'spend_30d': spend_30d,
                'spend_90d': spend_90d,
                'spend_ratio_30d_90d': spend_ratio_30d_90d,
                'spend_ratio_90d_180d': spend_ratio_90d_180d,
                'freq_30d': freq_30d,
                'freq_90d': freq_90d,
                'transactions_30d': transactions_30d,
                'transactions_90d': transactions_90d
            })
        
        momentum_df = pd.DataFrame(momentum_features)
        
        logger.info(f"Created momentum features for {len(momentum_df)} customers")
        
        return momentum_df
    
    def create_return_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create return-related features.
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            DataFrame with return features per customer
        """
        logger.info("Creating return features...")
        
        # Identify returns (negative quantities or InvoiceNo starting with 'C')
        df['is_return'] = (df['Quantity'] < 0) | (df['InvoiceNo'].str.startswith('C'))
        
        # Calculate return metrics per customer
        return_features = df.groupby('CustomerID').agg({
            'is_return': ['sum', 'mean'],
            'TotalAmount': 'sum'
        }).reset_index()
        
        # Flatten column names
        return_features.columns = ['CustomerID', 'total_returns', 'return_rate', 'total_amount']
        
        # Calculate return amount
        return_amount = df[df['is_return']].groupby('CustomerID')['TotalAmount'].sum().reset_index()
        return_amount.columns = ['CustomerID', 'return_amount']
        
        # Merge features
        return_features = return_features.merge(return_amount, on='CustomerID', how='left')
        return_features['return_amount'] = return_features['return_amount'].fillna(0)
        
        # Calculate net amount
        return_features['net_amount'] = return_features['total_amount'] - return_features['return_amount']
        
        logger.info(f"Created return features for {len(return_features)} customers")
        
        return return_features[['CustomerID', 'total_returns', 'return_rate', 
                              'return_amount', 'net_amount']]
    
    def create_geographic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create geographic features (country one-hot encoding).
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            DataFrame with geographic features per customer
        """
        logger.info("Creating geographic features...")
        
        # Get primary country per customer
        primary_country = df.groupby('CustomerID')['Country'].agg(
            lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
        ).reset_index()
        primary_country.columns = ['CustomerID', 'primary_country']
        
        # Create one-hot encoding
        country_dummies = pd.get_dummies(primary_country['primary_country'], prefix='country')
        geographic_features = pd.concat([primary_country[['CustomerID']], country_dummies], axis=1)
        
        logger.info(f"Created geographic features for {len(geographic_features)} customers")
        
        return geographic_features
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features (day of week, month, seasonality).
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            DataFrame with temporal features per customer
        """
        logger.info("Creating temporal features...")
        
        # Add temporal columns
        df_temp = df.copy()
        df_temp['day_of_week'] = df_temp['InvoiceDate'].dt.dayofweek
        df_temp['month'] = df_temp['InvoiceDate'].dt.month
        df_temp['quarter'] = df_temp['InvoiceDate'].dt.quarter
        df_temp['is_weekend'] = df_temp['day_of_week'].isin([5, 6]).astype(int)
        
        # Calculate temporal patterns per customer
        temporal_features = df_temp.groupby('CustomerID').agg({
            'day_of_week': ['mean', 'std'],
            'month': ['mean', 'std'],
            'is_weekend': 'mean',
            'InvoiceDate': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        temporal_features.columns = ['CustomerID', 'avg_day_of_week', 'std_day_of_week',
                                   'avg_month', 'std_month', 'weekend_ratio',
                                   'first_purchase_date', 'last_purchase_date']
        
        # Calculate customer lifetime
        temporal_features['customer_lifetime_days'] = (
            temporal_features['last_purchase_date'] - temporal_features['first_purchase_date']
        ).dt.days
        
        logger.info(f"Created temporal features for {len(temporal_features)} customers")
        
        return temporal_features[['CustomerID', 'avg_day_of_week', 'std_day_of_week',
                                'avg_month', 'std_month', 'weekend_ratio',
                                'customer_lifetime_days']]
    
    def create_all_features(self, df: pd.DataFrame, reference_features: pd.DataFrame = None) -> pd.DataFrame:
        """
        Create all features for the dataset.
        
        Args:
            df: Transaction DataFrame
            reference_features: Reference DataFrame to ensure consistent feature columns
            
        Returns:
            DataFrame with all features per customer
        """
        logger.info("Creating all features...")
        
        # Create individual feature sets
        rfm_features = self.create_rfm_features(df)
        diversity_features = self.create_basket_diversity_features(df)
        momentum_features = self.create_momentum_features(df)
        return_features = self.create_return_features(df)
        geographic_features = self.create_geographic_features(df)
        temporal_features = self.create_temporal_features(df)
        
        # Merge all features
        all_features = rfm_features.merge(diversity_features, on='CustomerID', how='left')
        all_features = all_features.merge(momentum_features, on='CustomerID', how='left')
        all_features = all_features.merge(return_features, on='CustomerID', how='left')
        all_features = all_features.merge(geographic_features, on='CustomerID', how='left')
        all_features = all_features.merge(temporal_features, on='CustomerID', how='left')
        
        # Fill missing values
        numeric_columns = all_features.select_dtypes(include=[np.number]).columns
        all_features[numeric_columns] = all_features[numeric_columns].fillna(0)
        
        # Align features with reference if provided
        if reference_features is not None:
            # Get all possible country columns from reference
            country_columns = [col for col in reference_features.columns if col.startswith('country_')]
            
            # Add missing country columns with zeros
            for col in country_columns:
                if col not in all_features.columns:
                    all_features[col] = 0
            
            # Remove extra country columns not in reference
            extra_country_columns = [col for col in all_features.columns 
                                   if col.startswith('country_') and col not in country_columns]
            all_features = all_features.drop(columns=extra_country_columns)
            
            # Ensure same column order as reference
            reference_columns = reference_features.columns.tolist()
            available_columns = [col for col in reference_columns if col in all_features.columns]
            all_features = all_features[available_columns]
        
        logger.info(f"Created {len(all_features.columns)} features for {len(all_features)} customers")
        
        return all_features
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of all feature names.
        
        Returns:
            List of feature names
        """
        return [
            # RFM features
            'recency_days', 'frequency', 'monetary', 'total_monetary',
            'total_transactions', 'unique_invoices',
            
            # Basket diversity
            'unique_products', 'unique_descriptions', 'avg_basket_size', 'avg_basket_value',
            
            # Momentum features
            'spend_30d', 'spend_90d', 'spend_ratio_30d_90d', 'spend_ratio_90d_180d',
            'freq_30d', 'freq_90d', 'transactions_30d', 'transactions_90d',
            
            # Return features
            'total_returns', 'return_rate', 'return_amount', 'net_amount',
            
            # Geographic features (will be added dynamically)
            # Temporal features
            'avg_day_of_week', 'std_day_of_week', 'avg_month', 'std_month',
            'weekend_ratio', 'customer_lifetime_days'
        ]
