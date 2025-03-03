#!/usr/bin/env python
import json
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction

from lambda_source import lambda_source
from s3_buckets import s3_buckets
from permission import lambda_permission, apigw_permission
from apigw import apigw


s3_policy_data = {
    "Version": "2012-10-17",
    "Statement": [],
}
lambda_role_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Effect": "Allow",
            "Sid": "assume",
        }
    ],
}

s3list = ["bucket142656345", "bucket2252454324"]


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS", region="us-east-1")

        [bucket, lambda_archive] = lambda_source(self)

        s3_buckets(self, s3list)

        role = lambda_permission(self, s3list)

        lambda_func = LambdaFunction(
            self,
            "lambda",
            function_name="lambda",
            s3_bucket=bucket.bucket,
            s3_key=lambda_archive.key,
            handler="index.handler",
            runtime="nodejs18.x",
            role=role.arn,
            environment={"variables": {"BUCKET_NAME": s3list[0]}},
        )
        rest_api, stage = apigw(self, lambda_func)
        apigw_permission(self, rest_api, lambda_func)

        TerraformOutput(self, "ApiUrl", value=stage.invoke_url)


app = App()
MyStack(app, "cdktf")

app.synth()
