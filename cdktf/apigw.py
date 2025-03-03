from cdktf_cdktf_provider_aws.api_gateway_rest_api import ApiGatewayRestApi
from cdktf_cdktf_provider_aws.api_gateway_resource import ApiGatewayResource
from cdktf_cdktf_provider_aws.api_gateway_method import ApiGatewayMethod
from cdktf_cdktf_provider_aws.api_gateway_integration import ApiGatewayIntegration
from cdktf_cdktf_provider_aws.api_gateway_deployment import ApiGatewayDeployment
from cdktf_cdktf_provider_aws.api_gateway_stage import ApiGatewayStage


def apigw(stack, lambda_func):

    rest_api = ApiGatewayRestApi(
        stack,
        "MyRestApi",
        name="my-rest-api",
        description="My REST API description",
    )

    resource = ApiGatewayResource(
        stack,
        "MyResource",
        rest_api_id=rest_api.id,
        parent_id=rest_api.root_resource_id,
        path_part="{proxy+}",
    )
    method = ApiGatewayMethod(
        stack,
        "method",
        rest_api_id=rest_api.id,
        http_method="ANY",
        resource_id=resource.id,
        authorization="NONE",
    )
    integration = ApiGatewayIntegration(
        stack,
        "integration",
        rest_api_id=rest_api.id,
        resource_id=resource.id,
        http_method=method.http_method,
        integration_http_method="POST",
        type="AWS_PROXY",
        uri=lambda_func.invoke_arn,
    )

    methodroot = ApiGatewayMethod(
        stack,
        "methodroot",
        rest_api_id=rest_api.id,
        http_method="ANY",
        resource_id=rest_api.root_resource_id,
        authorization="NONE",
    )
    integrationroot = ApiGatewayIntegration(
        stack,
        "integrationroot",
        rest_api_id=rest_api.id,
        resource_id=rest_api.root_resource_id,
        http_method=methodroot.http_method,
        integration_http_method="POST",
        type="AWS_PROXY",
        uri=lambda_func.invoke_arn,
    )

    deploy = ApiGatewayDeployment(
        stack,
        "deployment",
        rest_api_id=rest_api.id,
        depends_on=[integration, integrationroot],
    )
    stage = ApiGatewayStage(
        stack,
        "deploymentstage",
        rest_api_id=rest_api.id,
        deployment_id=deploy.id,
        stage_name="work",
    )

    return rest_api, stage
