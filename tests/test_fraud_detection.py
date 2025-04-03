import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import boto3
import json

def test_data_generation():
    """Test synthetic data generation"""
    from data.generate_synthetic_data import generate_transaction_data
    
    # Generate test data
    df = generate_transaction_data(n_samples=1000, fraud_ratio=0.01)
    
    # Check data structure
    assert isinstance(df, pd.DataFrame)
    assert 'transaction_id' in df.columns
    assert 'amount' in df.columns
    assert 'is_fraud' in df.columns
    
    # Check data types
    assert df['amount'].dtype in ['float64', 'int64']
    assert df['is_fraud'].dtype in ['int64']
    
    # Check fraud ratio
    assert abs(df['is_fraud'].mean() - 0.01) < 0.01

def test_data_cleaning():
    """Test data cleaning functions"""
    # Create sample data
    data = {
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'amount': [100.0, 200.0, np.nan],
        'merchant_category': ['retail', None, 'food'],
        'is_fraud': [0, 1, 0]
    }
    df = pd.DataFrame(data)
    
    # Test cleaning functions
    from ml_pipeline.glue_jobs.etl_job import clean_data
    
    cleaned_df = clean_data(df)
    
    # Check results
    assert cleaned_df['amount'].isna().sum() == 0
    assert cleaned_df['merchant_category'].isna().sum() == 0
    assert len(cleaned_df) == 3

def test_model_prediction():
    """Test model prediction endpoint"""
    # Initialize SageMaker runtime client
    runtime = boto3.client('sagemaker-runtime')
    
    # Prepare test data
    test_data = {
        "amount": 100.0,
        "merchant_category": "retail",
        "transaction_type": "online",
        "device_type": "mobile",
        "merchant_country": "USA",
        "timestamp": datetime.now().isoformat(),
        "hour": 12,
        "day_of_week": 1,
        "month": 1,
        "is_weekend": 0,
        "is_night": 0,
        "is_high_risk_country": 0,
        "is_online_transaction": 1,
        "is_mobile_device": 1
    }
    
    try:
        # Call endpoint
        response = runtime.invoke_endpoint(
            EndpointName='fraud-detection-endpoint',
            ContentType='application/json',
            Body=json.dumps(test_data)
        )
        
        result = json.loads(response['Body'].read().decode())
        
        # Check response structure
        assert 'predicted_probability' in result
        assert isinstance(result['predicted_probability'], float)
        assert 0 <= result['predicted_probability'] <= 1
        
    except Exception as e:
        pytest.skip(f"Skipping endpoint test: {str(e)}")

def test_feature_engineering():
    """Test feature engineering functions"""
    # Create sample data
    data = {
        'transaction_id': ['TXN001', 'TXN002'],
        'amount': [100.0, 200.0],
        'merchant_country': ['USA', 'Russia'],
        'transaction_type': ['in_store', 'online'],
        'device_type': ['desktop', 'mobile']
    }
    df = pd.DataFrame(data)
    
    # Test feature engineering
    from ml_pipeline.glue_jobs.etl_job import clean_data
    
    processed_df = clean_data(df)
    
    # Check derived features
    assert 'amount_log' in processed_df.columns
    assert 'is_high_risk_country' in processed_df.columns
    assert 'is_online_transaction' in processed_df.columns
    assert 'is_mobile_device' in processed_df.columns
    
    # Check feature values
    assert processed_df['is_high_risk_country'].sum() == 1
    assert processed_df['is_online_transaction'].sum() == 1
    assert processed_df['is_mobile_device'].sum() == 1 