output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.data_bucket.id
}

output "sagemaker_role_arn" {
  description = "ARN of the SageMaker execution role"
  value       = aws_iam_role.sagemaker_role.arn
}

output "sagemaker_notebook_url" {
  description = "URL of the SageMaker notebook instance"
  value       = "https://${aws_sagemaker_notebook_instance.fraud_detection.id}.notebook.${var.aws_region}.sagemaker.aws"
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.sagemaker_vpc.id
}

output "subnet_ids" {
  description = "IDs of the subnets"
  value       = aws_subnet.sagemaker_subnet[*].id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.sagemaker_sg.id
} 