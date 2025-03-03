#!/usr/bin/env python
import json
from constructs import Construct
from cdktf import App, TerraformStack, TerraformAsset, AssetType, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
from cdktf_cdktf_provider_aws.s3_object import S3Object
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_policy import IamPolicy
from cdktf_cdktf_provider_aws.iam_role_policy_attachment import IamRolePolicyAttachment
from cdktf_cdktf_provider_aws.api_gateway_rest_api import ApiGatewayRestApi
from cdktf_cdktf_provider_aws.api_gateway_resource import ApiGatewayResource
from cdktf_cdktf_provider_aws.api_gateway_method import ApiGatewayMethod
from cdktf_cdktf_provider_aws.api_gateway_integration import ApiGatewayIntegration
from cdktf_cdktf_provider_aws.api_gateway_deployment import ApiGatewayDeployment
from cdktf_cdktf_provider_aws.api_gateway_stage import ApiGatewayStage


lambda_resource_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {"ArnLike": {"AWS:SourceArn": "arn:aws:execute-api:us-east-1:207567791269:*"}}
    ],
}
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


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS", region="us-east-1")

        # Create Lambda executable
        asset = TerraformAsset(
            self, "lambda-asset", path="lib/lambda-handler/", type=AssetType.ARCHIVE
        )

        # Create unique S3 bucket that hosts Lambda executable
        bucket = S3Bucket(
            self,
            "bucket32432",
            bucket_prefix="cdktf-lambda",
        )

        # Upload Lambda zip file to newly created S3 bucket
        lambdaArchive = S3Object(
            self,
            "lambda-archive",
            bucket=bucket.bucket,
            key=asset.file_name,
            source=asset.path,
        )

        s3list = ["bucket142656345", "bucket2252454324"]

        s3objects = []
        for s3_name in s3list:
            s3object = S3Bucket(self, s3_name, bucket=s3_name)
            s3objects.append(s3object)
            s3_policy_data["Statement"].append(
                {
                    "Effect": "Allow",
                    "Action": ["s3:Get*", "s3:List*"],
                    "Resource": f"arn:aws:s3:::{s3_name}*",
                    "Sid": f"Sid{s3_name}",
                }
            )

        role = IamRole(
            self,
            "lambda-exec",
            name="lambda-role",
            assume_role_policy=json.dumps(lambda_role_policy),
        )

        IamRolePolicyAttachment(
            self,
            "lambda-managed-policy",
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            role=role.name,
        )
        s3_policy = IamPolicy(
            self, "lambda-s3-access", policy=json.dumps(s3_policy_data)
        )
        IamRolePolicyAttachment(
            self,
            "lambda-s3-policy",
            policy_arn=s3_policy.arn,
            role=role.name,
        )

        lambdaFunc = LambdaFunction(
            self,
            "lambda",
            function_name="lambda",
            s3_bucket=bucket.bucket,
            s3_key=lambdaArchive.key,
            handler="index.handler",
            runtime="nodejs18.x",
            role=role.arn,
            environment={"variables": {"BUCKET_NAME": s3list[0]}},
        )

        rest_api = ApiGatewayRestApi(
            self,
            "MyRestApi",
            name="my-rest-api",
            description="My REST API description",
        )

        lambda_permission = LambdaPermission(
            self,
            "lambda-permission",
            function_name=lambdaFunc.function_name,
            action="lambda:InvokeFunction",
            principal="apigateway.amazonaws.com",
            source_arn=rest_api.execution_arn + "*",
        )

        resource = ApiGatewayResource(
            self,
            "MyResource",
            rest_api_id=rest_api.id,
            parent_id=rest_api.root_resource_id,
            path_part="{proxy+}",
        )
        method = ApiGatewayMethod(
            self,
            "method",
            rest_api_id=rest_api.id,
            http_method="ANY",
            resource_id=resource.id,
            authorization="NONE",
        )
        integration = ApiGatewayIntegration(
            self,
            "integration",
            rest_api_id=rest_api.id,
            resource_id=resource.id,
            http_method=method.http_method,
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=lambdaFunc.invoke_arn,
        )

        methodroot = ApiGatewayMethod(
            self,
            "methodroot",
            rest_api_id=rest_api.id,
            http_method="ANY",
            resource_id=rest_api.root_resource_id,
            authorization="NONE",
        )
        integrationroot = ApiGatewayIntegration(
            self,
            "integrationroot",
            rest_api_id=rest_api.id,
            resource_id=rest_api.root_resource_id,
            http_method=methodroot.http_method,
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=lambdaFunc.invoke_arn,
        )

        deploy = ApiGatewayDeployment(
            self,
            "deployment",
            rest_api_id=rest_api.id,
            depends_on=[integration, integrationroot],
        )
        stage = ApiGatewayStage(
            self,
            "deploymentstage",
            rest_api_id=rest_api.id,
            deployment_id=deploy.id,
            stage_name="work",
        )

        # fn.add_environment("BUCKET_NAME", s3objects[0].bucket_name)

        # api = apigateway.LambdaRestApi(self, "api", handler=fn)
        TerraformOutput(self, "ApiUrl", value=stage.invoke_url)


app = App()
MyStack(app, "cdktf")

app.synth()
