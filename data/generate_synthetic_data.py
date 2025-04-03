import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()

def generate_transaction_data(n_samples=10000, fraud_ratio=0.01):
    """
    Generate synthetic credit card transaction data with realistic fraud patterns
    """
    # Generate base transaction data
    data = {
        'transaction_id': [f'TXN{i:08d}' for i in range(n_samples)],
        'timestamp': [fake.date_time_between(start_date='-30d', end_date='now') for _ in range(n_samples)],
        'amount': np.random.lognormal(mean=4, sigma=1, size=n_samples),
        'merchant_category': np.random.choice(['retail', 'food', 'travel', 'entertainment', 'utilities'], size=n_samples),
        'card_number': [fake.credit_card_number() for _ in range(n_samples)],
        'cardholder_name': [fake.name() for _ in range(n_samples)],
        'cardholder_address': [fake.address() for _ in range(n_samples)],
        'merchant_name': [fake.company() for _ in range(n_samples)],
        'merchant_city': [fake.city() for _ in range(n_samples)],
        'merchant_country': [fake.country() for _ in range(n_samples)],
        'transaction_type': np.random.choice(['online', 'in_store', 'atm'], size=n_samples),
        'device_type': np.random.choice(['mobile', 'desktop', 'pos_terminal', 'atm'], size=n_samples),
        'ip_address': [fake.ipv4() for _ in range(n_samples)],
        'is_fraud': np.zeros(n_samples, dtype=int)
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Generate fraud cases
    n_fraud = int(n_samples * fraud_ratio)
    fraud_indices = np.random.choice(n_samples, n_fraud, replace=False)
    
    # Add fraud patterns
    for idx in fraud_indices:
        # Randomly modify some features to indicate fraud
        df.loc[idx, 'is_fraud'] = 1
        df.loc[idx, 'amount'] *= np.random.uniform(2, 10)  # Larger amounts
        df.loc[idx, 'merchant_country'] = np.random.choice(['Russia', 'China', 'Nigeria', 'Brazil'])  # High-risk countries
        df.loc[idx, 'device_type'] = 'mobile'  # Mobile transactions are more common in fraud
        df.loc[idx, 'transaction_type'] = 'online'  # Online transactions are more common in fraud
    
    # Add derived features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
    
    # Add some noise to make the data more realistic
    df['amount'] = df['amount'].round(2)
    
    return df

def save_data(df, output_path):
    """
    Save the generated data to CSV
    """
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    # Generate training data
    train_data = generate_transaction_data(n_samples=100000, fraud_ratio=0.01)
    save_data(train_data, 'data/raw/train_data.csv')
    
    # Generate test data
    test_data = generate_transaction_data(n_samples=20000, fraud_ratio=0.01)
    save_data(test_data, 'data/raw/test_data.csv')
    
    print("Data generation completed!")
    print(f"Training data shape: {train_data.shape}")
    print(f"Test data shape: {test_data.shape}")
    print(f"Fraud ratio in training: {train_data['is_fraud'].mean():.4f}")
    print(f"Fraud ratio in test: {test_data['is_fraud'].mean():.4f}") 