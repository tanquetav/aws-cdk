import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_project.cdk_project_stack import CdkProjectStack


# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_project/cdk_project_stack.py
def test_infra_created():
    app = core.App()
    stack = CdkProjectStack(app, "cdk-project")
    template = assertions.Template.from_stack(stack)
    template.resource_properties_count_is("AWS::S3::Bucket", {}, 2)
    template.resource_properties_count_is("AWS::ApiGateway::RestApi", {}, 1)
    template.resource_properties_count_is("AWS::Lambda::Function", {}, 1)
