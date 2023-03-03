#!/usr/bin/env python3

from aws_cdk import App

from sbifpt_aws_dev_ops_test.vpc_stack import CdkVpcStack
from sbifpt_aws_dev_ops_test.ec2_stack import CdkEc2Stack
from sbifpt_aws_dev_ops_test.lambda_zipfile_stack import LambdaZipFileStack

app = App()

vpc_stack = CdkVpcStack(app, "cdk-vpc")
ec2_stack = CdkEc2Stack(app, "cdk-ec2",
                        vpc=vpc_stack.vpc)
lambda_stack = LambdaZipFileStack(app, "cdk-lambda")


app.synth()