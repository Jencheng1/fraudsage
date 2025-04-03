#!/usr/bin/env python3
import aws_cdk as cdk
from fraud_detection_stack import FraudDetectionStack

app = cdk.App()
FraudDetectionStack(app, "FraudDetectionStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region")
    )
)

app.synth() 