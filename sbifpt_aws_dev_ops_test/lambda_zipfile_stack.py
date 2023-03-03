from aws_cdk import CfnOutput, Stack, Duration
import aws_cdk.aws_lambda as lambdaFunc
import aws_cdk.aws_iam as iam
from constructs import Construct

class LambdaZipFileStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open("./lambda/lambda-handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        # Create Lambda function
        lambda_function = lambdaFunc.Function(self, "lambda_function",
            runtime=lambdaFunc.Runtime.PYTHON_3_9,
            handler="index.lambda_handler",
            code=lambdaFunc.InlineCode(handler_code),
            timeout=Duration.seconds(900)
            )

        assert lambda_function.role is not None
        lambda_function.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        lambda_function.role.add_to_policy(
            iam.PolicyStatement(
                effect = iam.Effect.ALLOW,
                actions = [
                    "ssm:SendCommand",
                    "ssm:ListCommands",
                    "ssm:DescribeInstanceInformation",
                    "ssm:GetCommandInvocation"
                ],
                resources = ['*']
            )
        )

        CfnOutput(self,"LambdaName",
            value=lambda_function.function_name,
            description="Lambda Function for zipFile",
            export_name="LambdaName")
