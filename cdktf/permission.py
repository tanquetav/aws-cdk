import json

from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_policy import IamPolicy
from cdktf_cdktf_provider_aws.iam_role_policy_attachment import IamRolePolicyAttachment
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission

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


def lambda_permission(stack, s3list):
    role = IamRole(
        stack,
        "lambda-exec",
        name="lambda-role",
        assume_role_policy=json.dumps(lambda_role_policy),
    )

    # Managed Role para permitir gravar no cloudwatch
    IamRolePolicyAttachment(
        stack,
        "lambda-managed-policy",
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        role=role.name,
    )

    # Role para acessar o s3
    for s3_name in s3list:
        s3_policy_data["Statement"].append(
            {
                "Effect": "Allow",
                "Action": ["s3:Get*", "s3:List*"],
                "Resource": f"arn:aws:s3:::{s3_name}*",
                "Sid": f"Sid{s3_name}",
            }
        )
    s3_policy = IamPolicy(stack, "lambda-s3-access", policy=json.dumps(s3_policy_data))
    IamRolePolicyAttachment(
        stack,
        "lambda-s3-policy",
        policy_arn=s3_policy.arn,
        role=role.name,
    )

    return role


def apigw_permission(stack, rest_api, lambdaFunc):
    LambdaPermission(
        stack,
        "lambda-permission",
        function_name=lambdaFunc.function_name,
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        source_arn=rest_api.execution_arn + "*",
    )
