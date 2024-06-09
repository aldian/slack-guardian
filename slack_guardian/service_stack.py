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

        # Resource and Methods
        commands_resource = api.root.add_resource("commands")
        commands_resource.add_method("GET", apigw.LambdaIntegration(command_processor_lambda))
        commands_resource.add_method("POST", apigw.LambdaIntegration(command_processor_lambda))

        events_resource = api.root.add_resource("events")
        events_resource.add_method("POST", apigw.LambdaIntegration(event_processor_lambda))