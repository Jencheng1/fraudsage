import streamlit as st
import pandas as pd
import numpy as np
import boto3
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
s3 = boto3.client('s3')

# Page configuration
st.set_page_config(
    page_title="Credit Card Fraud Detection",
    page_icon="🔒",
    layout="wide"
)

# Title and description
st.title("Credit Card Fraud Detection System")
st.markdown("""
This application uses AWS SageMaker Autopilot to detect fraudulent credit card transactions in real-time.
""")

# Sidebar
st.sidebar.header("Transaction Details")

# Input form
with st.sidebar.form("transaction_form"):
    amount = st.number_input("Transaction Amount ($)", min_value=0.0, max_value=100000.0)
    merchant_category = st.selectbox(
        "Merchant Category",
        ["retail", "food", "travel", "entertainment", "utilities"]
    )
    transaction_type = st.selectbox(
        "Transaction Type",
        ["online", "in_store", "atm"]
    )
    device_type = st.selectbox(
        "Device Type",
        ["mobile", "desktop", "pos_terminal", "atm"]
    )
    merchant_country = st.text_input("Merchant Country")
    submit_button = st.form_submit_button("Check for Fraud")

# Main content
if submit_button:
    # Prepare input data
    input_data = {
        "amount": amount,
        "merchant_category": merchant_category,
        "transaction_type": transaction_type,
        "device_type": device_type,
        "merchant_country": merchant_country,
        "timestamp": datetime.now().isoformat(),
        "hour": datetime.now().hour,
        "day_of_week": datetime.now().weekday(),
        "month": datetime.now().month,
        "is_weekend": 1 if datetime.now().weekday() >= 5 else 0,
        "is_night": 1 if datetime.now().hour >= 22 or datetime.now().hour <= 5 else 0,
        "is_high_risk_country": 1 if merchant_country in ["Russia", "China", "Nigeria", "Brazil"] else 0,
        "is_online_transaction": 1 if transaction_type == "online" else 0,
        "is_mobile_device": 1 if device_type == "mobile" else 0
    }
    
    # Call SageMaker endpoint
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='fraud-detection-endpoint',
            ContentType='application/json',
            Body=json.dumps(input_data)
        )
        
        result = json.loads(response['Body'].read().decode())
        fraud_probability = result['predicted_probability']
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Fraud Detection Result")
            if fraud_probability > 0.5:
                st.error(f"⚠️ High Risk Transaction! (Probability: {fraud_probability:.2%})")
            else:
                st.success(f"✅ Low Risk Transaction (Probability: {fraud_probability:.2%})")
        
        with col2:
            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=fraud_probability * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [0, 100]},
                      'bar': {'color': "darkblue"},
                      'steps': [
                          {'range': [0, 50], 'color': "lightgray"},
                          {'range': [50, 100], 'color': "gray"}
                      ],
                      'threshold': {
                          'line': {'color': "red", 'width': 4},
                          'thickness': 0.75,
                          'value': fraud_probability * 100
                      }
                      }
            ))
            fig.update_layout(height=250, margin={'l': 10, 'r': 10, 't': 10, 'b': 10})
            st.plotly_chart(fig)
        
        # Display transaction details
        st.subheader("Transaction Details")
        details_df = pd.DataFrame([input_data])
        st.dataframe(details_df)
        
    except Exception as e:
        st.error(f"Error calling SageMaker endpoint: {str(e)}")

# Add historical data visualization
st.subheader("Historical Fraud Detection Statistics")
try:
    # Load historical data from S3
    response = s3.get_object(
        Bucket='your-bucket',
        Key='data/processed/historical_stats.json'
    )
    historical_data = json.loads(response['Body'].read().decode())
    
    # Create time series plot
    fig = px.line(
        historical_data,
        x='date',
        y='fraud_rate',
        title='Historical Fraud Rate'
    )
    st.plotly_chart(fig)
    
    # Display summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Average Fraud Rate",
            f"{historical_data['avg_fraud_rate']:.2%}"
        )
    with col2:
        st.metric(
            "Total Transactions",
            f"{historical_data['total_transactions']:,}"
        )
    with col3:
        st.metric(
            "Detected Fraud Cases",
            f"{historical_data['detected_fraud']:,}"
        )
    
except Exception as e:
    st.warning("Historical data not available")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Powered by AWS SageMaker Autopilot | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True) 