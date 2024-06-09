from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)


class SlackGuardianStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Lambda Functions
        event_processor_lambda = _lambda.Function(
            self, "EventProcessor",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambdas"),
            handler="event_processor.handler",
        )
        command_processor_lambda = _lambda.Function(
            self, "CommandHandler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambdas"),
            handler="command_handler.handler",
        )

        # API Gateway
        api = apigw.RestApi(self, "LambdaRestApi")

        # API Key
        api_key = api.add_api_key("ApiKey")

        # Usage Plan
        plan = api.add_usage_plan("UsagePlan",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,  # Requests per second
                burst_limit=2 
            )
        )

         # Associate API Key with Usage Plan
        plan.add_api_key(api_key)

        # Associate Usage Plan with API Stages
        plan.add_api_stage(
            stage=api.deployment_stage
        )

        # Resource and Methods
        commands_resource = api.root.add_resource("commands")
        commands_resource.add_method(
            "GET", apigw.LambdaIntegration(command_processor_lambda),
            api_key_required=True,
        )
        commands_resource.add_method(
            "POST", apigw.LambdaIntegration(command_processor_lambda),
            api_key_required=True,
        )

        events_resource = api.root.add_resource("events")
        events_resource.add_method(
            "POST", apigw.LambdaIntegration(event_processor_lambda),
            api_key_required=True,
        )