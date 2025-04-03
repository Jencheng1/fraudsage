import boto3
import sagemaker
from sagemaker.automl.automl import AutoML
from sagemaker.automl.automl_inputs import AutoMLInput
from sagemaker.inputs import TrainingInput

def create_autopilot_job():
    # Initialize SageMaker client
    sagemaker_client = boto3.client('sagemaker')
    
    # Define job configuration
    job_config = {
        'ProblemType': 'BinaryClassification',
        'AutoMLJobObjective': {
            'MetricName': 'AUC'
        },
        'AutoMLJobConfig': {
            'CompletionCriteria': {
                'MaxCandidates': 100,
                'MaxTimePerTrainingJobInSeconds': 3600,
                'MaxAutoMLJobRuntimeInSeconds': 86400
            },
            'SecurityConfig': {
                'EnableInterContainerTrafficEncryption': True,
                'VpcConfig': {
                    'SecurityGroupIds': ['sg-xxxxxxxx'],
                    'Subnets': ['subnet-xxxxxxxx']
                }
            }
        },
        'RoleArn': 'arn:aws:iam::xxxxxxxx:role/service-role/AmazonSageMaker-ExecutionRole',
        'InputDataConfig': [
            {
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'Parquet',
                        'S3Uri': 's3://your-bucket/data/processed/train/'
                    }
                },
                'TargetAttributeName': 'is_fraud'
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': 's3://your-bucket/models/autopilot/'
        }
    }
    
    # Create AutoML job
    response = sagemaker_client.create_auto_ml_job(
        AutoMLJobName='fraud-detection-autopilot',
        **job_config
    )
    
    return response

def create_autopilot_model():
    # Initialize SageMaker client
    sagemaker_client = boto3.client('sagemaker')
    
    # Define model configuration
    model_config = {
        'ModelName': 'fraud-detection-model',
        'ExecutionRoleArn': 'arn:aws:iam::xxxxxxxx:role/service-role/AmazonSageMaker-ExecutionRole',
        'PrimaryContainer': {
            'Image': '683313688378.dkr.ecr.us-east-1.amazonaws.com/autopilot:1.0-cpu-py3',
            'ModelDataUrl': 's3://your-bucket/models/autopilot/best-candidate/'
        }
    }
    
    # Create model
    response = sagemaker_client.create_model(**model_config)
    
    return response

def create_endpoint_config():
    # Initialize SageMaker client
    sagemaker_client = boto3.client('sagemaker')
    
    # Define endpoint configuration
    endpoint_config = {
        'EndpointConfigName': 'fraud-detection-endpoint-config',
        'ProductionVariants': [
            {
                'VariantName': 'AllTraffic',
                'ModelName': 'fraud-detection-model',
                'InstanceType': 'ml.m5.xlarge',
                'InitialInstanceCount': 1
            }
        ]
    }
    
    # Create endpoint configuration
    response = sagemaker_client.create_endpoint_config(**endpoint_config)
    
    return response

def create_endpoint():
    # Initialize SageMaker client
    sagemaker_client = boto3.client('sagemaker')
    
    # Define endpoint configuration
    endpoint_config = {
        'EndpointName': 'fraud-detection-endpoint',
        'EndpointConfigName': 'fraud-detection-endpoint-config'
    }
    
    # Create endpoint
    response = sagemaker_client.create_endpoint(**endpoint_config)
    
    return response

if __name__ == "__main__":
    # Create AutoML job
    job_response = create_autopilot_job()
    print("AutoML job created:", job_response)
    
    # Create model
    model_response = create_autopilot_model()
    print("Model created:", model_response)
    
    # Create endpoint configuration
    endpoint_config_response = create_endpoint_config()
    print("Endpoint configuration created:", endpoint_config_response)
    
    # Create endpoint
    endpoint_response = create_endpoint()
    print("Endpoint created:", endpoint_response) 