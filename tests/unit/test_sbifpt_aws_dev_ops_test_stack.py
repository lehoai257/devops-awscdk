import aws_cdk as core
import aws_cdk.assertions as assertions

from sbifpt_aws_dev_ops_test.sbifpt_aws_dev_ops_test_stack import SbifptAwsDevOpsTestStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sbifpt_aws_dev_ops_test/sbifpt_aws_dev_ops_test_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SbifptAwsDevOpsTestStack(app, "sbifpt-aws-dev-ops-test")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
