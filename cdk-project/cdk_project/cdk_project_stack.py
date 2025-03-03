from aws_cdk import (
    # Duration,
    RemovalPolicy,
    CfnOutput,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    # aws_sqs as sqs,
)
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement


class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        s3list = ["bucket1", "bucket2"]

        fn = _lambda.Function(
            self,
            "MyFunction",
            runtime=_lambda.Runtime.NODEJS_LATEST,
            handler="index.handler",
            code=_lambda.Code.from_asset("lib/lambda-handler"),
        )

        s3objects = []
        for s3_name in s3list:
            s3object = s3.Bucket(self, s3_name, removal_policy=RemovalPolicy.DESTROY)
            s3objects.append(s3object)
            fn.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["s3:Get*", "s3:List*"],
                    resources=[s3object.bucket_arn + "*"],
                )
            )
        fn.add_environment("BUCKET_NAME", s3objects[0].bucket_name)

        api = apigateway.LambdaRestApi(self, "api", handler=fn)
        CfnOutput(self, "ApiUrl", value=api.url)
