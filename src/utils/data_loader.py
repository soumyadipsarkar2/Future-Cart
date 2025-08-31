"""
Data loader utilities for the Online Retail dataset.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Data loader for Online Retail dataset."""
    
    def __init__(self, data_path: str = "data/Online Retail.csv"):
        """
        Initialize DataLoader.
        
        Args:
            data_path: Path to the Excel file
        """
        self.data_path = Path(data_path)
        self.data = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load the Online Retail dataset.
        
        Returns:
            DataFrame with the raw data
        """
        try:
            logger.info(f"Loading data from {self.data_path}")
            # Try CSV first, then Excel
            if str(self.data_path).endswith('.csv'):
                self.data = pd.read_csv(self.data_path)
            else:
                self.data = pd.read_excel(self.data_path)
            logger.info(f"Loaded {len(self.data)} rows and {len(self.data.columns)} columns")
            return self.data
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def basic_preprocessing(self, cutoff_date: str = "2011-09-01") -> pd.DataFrame:
        """
        Perform basic preprocessing on the dataset.
        
        Args:
            cutoff_date: Date to use as cutoff for prediction window
            
        Returns:
            Preprocessed DataFrame
        """
        if self.data is None:
            self.load_data()
            
        df = self.data.copy()
        
        # Convert InvoiceDate to datetime
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Handle missing CustomerID
        initial_rows = len(df)
        df = df.dropna(subset=['CustomerID'])
        logger.info(f"Dropped {initial_rows - len(df)} rows with missing CustomerID")
        
        # Convert CustomerID to int
        df['CustomerID'] = df['CustomerID'].astype(int)
        
        # Handle negative quantities (returns)
        df['is_return'] = df['Quantity'] < 0
        df['Quantity'] = df['Quantity'].abs()
        
        # Remove zero quantities
        df = df[df['Quantity'] > 0]
        
        # Calculate total amount
        df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
        
        # Filter by cutoff date
        cutoff_date = pd.to_datetime(cutoff_date)
        df = df[df['InvoiceDate'] <= cutoff_date]
        
        logger.info(f"After preprocessing: {len(df)} rows")
        logger.info(f"Unique customers: {df['CustomerID'].nunique()}")
        
        return df
    
    def create_labels(self, df: pd.DataFrame, prediction_window_days: int = 30) -> pd.DataFrame:
        """
        Create binary labels for purchase prediction.
        
        Args:
            df: Preprocessed DataFrame
            prediction_window_days: Number of days to look ahead
            
        Returns:
            DataFrame with customer-level labels
        """
        # Get the latest date for each customer
        customer_latest = df.groupby('CustomerID')['InvoiceDate'].max().reset_index()
        customer_latest.columns = ['CustomerID', 'last_purchase_date']
        
        # Calculate cutoff date for prediction window
        max_date = df['InvoiceDate'].max()
        prediction_cutoff = max_date - pd.Timedelta(days=prediction_window_days)
        
        # Find customers who made purchases in the prediction window
        future_purchases = df[
            (df['InvoiceDate'] > prediction_cutoff) & 
            (df['InvoiceDate'] <= max_date)
        ]['CustomerID'].unique()
        
        # Create labels
        labels = customer_latest.copy()
        labels['will_purchase'] = labels['CustomerID'].isin(future_purchases).astype(int)
        
        logger.info(f"Label distribution: {labels['will_purchase'].value_counts().to_dict()}")
        
        return labels
    
    def get_train_test_split(self, df: pd.DataFrame, test_size: float = 0.2, 
                           random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets by customer.
        
        Args:
            df: DataFrame with customer-level data
            test_size: Proportion of customers for test set
            random_state: Random seed
            
        Returns:
            Tuple of (train_df, test_df)
        """
        from sklearn.model_selection import train_test_split
        
        # Get unique customers
        customers = df['CustomerID'].unique()
        
        # Split customers
        train_customers, test_customers = train_test_split(
            customers, test_size=test_size, random_state=random_state, stratify=None
        )
        
        # Split data
        train_df = df[df['CustomerID'].isin(train_customers)]
        test_df = df[df['CustomerID'].isin(test_customers)]
        
        logger.info(f"Train set: {len(train_df)} rows, {len(train_customers)} customers")
        logger.info(f"Test set: {len(test_df)} rows, {len(test_customers)} customers")
        
        return train_df, test_df


def load_sample_data() -> pd.DataFrame:
    """
    Load sample data for testing purposes.
    
    Returns:
        Sample DataFrame
    """
    # Create sample data that mimics the Online Retail dataset structure
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'InvoiceNo': [f'INV{i:06d}' for i in range(1, n_samples + 1)],
        'StockCode': [f'PROD{i:04d}' for i in range(1, n_samples + 1)],
        'Description': [f'Product {i}' for i in range(1, n_samples + 1)],
        'Quantity': np.random.randint(1, 50, n_samples),
        'InvoiceDate': pd.date_range('2011-01-01', periods=n_samples, freq='D'),
        'UnitPrice': np.random.uniform(1, 100, n_samples),
        'CustomerID': np.random.randint(1000, 2000, n_samples),
        'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'EIRE'], n_samples)
    })
    
    # Add TotalAmount column
    sample_data['TotalAmount'] = sample_data['Quantity'] * sample_data['UnitPrice']
    
    return sample_data
