"""
Tests for data loader utilities.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.data_loader import DataLoader, load_sample_data


class TestDataLoader:
    """Test cases for DataLoader class."""
    
    def test_load_sample_data(self):
        """Test loading sample data."""
        data = load_sample_data()
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert 'CustomerID' in data.columns
        assert 'InvoiceDate' in data.columns
        assert 'TotalAmount' in data.columns
    
    def test_data_loader_initialization(self):
        """Test DataLoader initialization."""
        loader = DataLoader()
        assert loader.data_path is not None
        assert loader.data is None
    
    def test_basic_preprocessing_with_sample_data(self):
        """Test basic preprocessing with sample data."""
        # Create sample data
        sample_data = pd.DataFrame({
            'InvoiceNo': ['INV001', 'INV002'],
            'StockCode': ['PROD001', 'PROD002'],
            'Description': ['Product 1', 'Product 2'],
            'Quantity': [5, 3],
            'InvoiceDate': ['2011-01-01', '2011-01-02'],
            'UnitPrice': [10.0, 15.0],
            'CustomerID': [12345, 12345],
            'Country': ['UK', 'UK']
        })
        
        # Create temporary loader with sample data
        loader = DataLoader()
        loader.data = sample_data
        
        # Test preprocessing
        processed = loader.basic_preprocessing()
        
        assert isinstance(processed, pd.DataFrame)
        assert len(processed) > 0
        assert 'TotalAmount' in processed.columns
        assert 'is_return' in processed.columns
    
    def test_create_labels(self):
        """Test label creation."""
        # Create sample transaction data
        sample_data = pd.DataFrame({
            'CustomerID': [1, 1, 2, 2, 3],
            'InvoiceDate': [
                '2011-08-01', '2011-08-15',  # Customer 1: before cutoff
                '2011-08-01', '2011-08-15',  # Customer 2: before cutoff
                '2011-09-15'                 # Customer 3: after cutoff (will purchase)
            ]
        })
        sample_data['InvoiceDate'] = pd.to_datetime(sample_data['InvoiceDate'])
        
        # Create temporary loader
        loader = DataLoader()
        loader.data = sample_data
        
        # Test label creation
        labels = loader.create_labels(sample_data, prediction_window_days=30)
        
        assert isinstance(labels, pd.DataFrame)
        assert 'will_purchase' in labels.columns
        assert 'CustomerID' in labels.columns
        assert len(labels) == 3  # 3 unique customers


class TestLoadSampleData:
    """Test cases for load_sample_data function."""
    
    def test_sample_data_structure(self):
        """Test that sample data has correct structure."""
        data = load_sample_data()
        
        required_columns = [
            'InvoiceNo', 'StockCode', 'Description', 'Quantity',
            'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'
        ]
        
        for col in required_columns:
            assert col in data.columns
    
    def test_sample_data_types(self):
        """Test that sample data has correct data types."""
        data = load_sample_data()
        
        assert pd.api.types.is_datetime64_any_dtype(data['InvoiceDate'])
        assert pd.api.types.is_numeric_dtype(data['Quantity'])
        assert pd.api.types.is_numeric_dtype(data['UnitPrice'])
        assert pd.api.types.is_numeric_dtype(data['CustomerID'])
    
    def test_sample_data_quality(self):
        """Test that sample data has reasonable values."""
        data = load_sample_data()
        
        # Check for reasonable ranges
        assert data['Quantity'].min() > 0
        assert data['UnitPrice'].min() > 0
        assert data['CustomerID'].min() >= 1000
        assert data['CustomerID'].max() < 2000
        
        # Check for no missing values in key columns
        assert not data['CustomerID'].isnull().any()
        assert not data['InvoiceDate'].isnull().any()


if __name__ == "__main__":
    pytest.main([__file__])
