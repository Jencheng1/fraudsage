import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define input and output paths
input_path = "s3://your-bucket/data/raw/"
output_path = "s3://your-bucket/data/processed/"

# Read raw data
raw_data = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [input_path]},
    format="csv",
    format_options={"withHeader": True}
)

# Convert to Spark DataFrame
df = raw_data.toDF()

# Data cleaning and transformation
def clean_data(df):
    # Convert timestamp to datetime
    df = df.withColumn("timestamp", to_timestamp("timestamp"))
    
    # Handle missing values
    df = df.na.fill("unknown", ["merchant_category", "merchant_name", "merchant_city", "merchant_country"])
    df = df.na.fill(0, ["amount"])
    
    # Remove duplicates
    df = df.dropDuplicates(["transaction_id"])
    
    # Add derived features
    df = df.withColumn("hour", hour("timestamp"))
    df = df.withColumn("day_of_week", dayofweek("timestamp"))
    df = df.withColumn("month", month("timestamp"))
    df = df.withColumn("is_weekend", when(col("day_of_week").isin(6, 7), 1).otherwise(0))
    df = df.withColumn("is_night", when((col("hour") >= 22) | (col("hour") <= 5), 1).otherwise(0))
    
    # Feature engineering
    df = df.withColumn("amount_log", log(col("amount") + 1))
    df = df.withColumn("is_high_risk_country", 
                      when(col("merchant_country").isin(["Russia", "China", "Nigeria", "Brazil"]), 1)
                      .otherwise(0))
    df = df.withColumn("is_online_transaction", 
                      when(col("transaction_type") == "online", 1)
                      .otherwise(0))
    df = df.withColumn("is_mobile_device", 
                      when(col("device_type") == "mobile", 1)
                      .otherwise(0))
    
    # Select and order features
    feature_columns = [
        "transaction_id", "timestamp", "amount", "amount_log",
        "merchant_category", "merchant_name", "merchant_city",
        "merchant_country", "transaction_type", "device_type",
        "hour", "day_of_week", "month", "is_weekend", "is_night",
        "is_high_risk_country", "is_online_transaction", "is_mobile_device",
        "is_fraud"
    ]
    
    return df.select(feature_columns)

# Clean and transform data
cleaned_df = clean_data(df)

# Convert back to DynamicFrame
cleaned_dynamic_frame = DynamicFrame.fromDF(cleaned_df, glueContext, "cleaned_data")

# Write processed data
glueContext.write_dynamic_frame.from_options(
    frame=cleaned_dynamic_frame,
    connection_type="s3",
    connection_options={
        "path": output_path,
        "partitionKeys": ["merchant_category", "is_fraud"]
    },
    format="parquet"
)

# Job completion
job.commit() 