from aws_cdk import (
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sqs as sqs,
    CfnOutput,
    Stack,
)
from constructs import Construct


class SlackGuardianStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SQS Queue
        queue = sqs.Queue(self, "SlackEventQueue")

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
        safety_analyzer_lambda = _lambda.Function(
            self, "SafetyAnalyzer",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambdas"),
            handler="safety_analyzer.handler",
        )

        # Grant Lambda permissions
        queue.grant_send_messages(event_processor_lambda)  # For sending
        queue.grant_consume_messages(safety_analyzer_lambda)  # For consuming

        # Add SQS event source to safety_analyzer_lambda
        safety_analyzer_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(queue)
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