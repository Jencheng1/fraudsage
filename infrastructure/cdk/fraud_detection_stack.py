from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_sagemaker as sagemaker,
    aws_logs as logs
)
from constructs import Construct

class FraudSageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for data storage
        data_bucket = s3.Bucket(
            self, "FraudSageDataBucket",
            bucket_name=f"fraudsage-data-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            auto_delete_objects=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # IAM role for SageMaker
        sagemaker_role = iam.Role(
            self, "FraudSageExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com")
        )

        # Add S3 permissions to SageMaker role
        data_bucket.grant_read_write(sagemaker_role)

        # Add CloudWatch Logs permissions
        sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["arn:aws:logs:*:*:*"]
            )
        )

        # VPC for SageMaker
        vpc = ec2.Vpc(
            self, "FraudSageVPC",
            max_azs=3,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                )
            ]
        )

        # Security group for SageMaker
        security_group = ec2.SecurityGroup(
            self, "FraudSageSecurityGroup",
            vpc=vpc,
            description="Security group for SageMaker endpoints",
            allow_all_outbound=True
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443)
        )

        # SageMaker Notebook Instance
        notebook = sagemaker.CfnNotebookInstance(
            self, "FraudSageNotebook",
            notebook_instance_name="fraudsage-notebook",
            role_arn=sagemaker_role.role_arn,
            instance_type="ml.t3.medium",
            subnet_id=vpc.private_subnets[0].subnet_id,
            security_groups=[security_group.security_group_id],
            direct_internet_access=False,
            tags=[
                cdk.CfnTag(key="Environment", value="dev"),
                cdk.CfnTag(key="Project", value="fraudsage")
            ]
        )

        # CloudWatch Log Group
        log_group = logs.LogGroup(
            self, "FraudSageLogGroup",
            log_group_name="/aws/sagemaker/fraudsage",
            retention=logs.RetentionDays.THIRTY_DAYS,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Outputs
        cdk.CfnOutput(self, "DataBucketName", value=data_bucket.bucket_name)
        cdk.CfnOutput(self, "SageMakerRoleArn", value=sagemaker_role.role_arn)
        cdk.CfnOutput(self, "VpcId", value=vpc.vpc_id)
        cdk.CfnOutput(self, "SecurityGroupId", value=security_group.security_group_id)
        cdk.CfnOutput(self, "NotebookUrl", 
                     value=f"https://{notebook.notebook_instance_name}.notebook.{self.region}.sagemaker.aws") 