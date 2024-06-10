from aws_cdk import (
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
    aws_sqs as sqs,
    CfnOutput,
    Stack,
)
from constructs import Construct


class SlackGuardianStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        queue = sqs.Queue(self, "SlackEventQueue")

        # DynamoDB Table
        analysis_results_table = dynamodb.Table(
            self, "AnalysisResultsTable",
            partition_key=dynamodb.Attribute(
                name="MessageId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="Timestamp", type=dynamodb.AttributeType.NUMBER),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # For cost-effective scaling
        )

        slack_secret_arn = ssm.StringParameter.value_for_string_parameter(
            self,
            "/slack-guardian/slack-verification-token-arn",
        )

        # Lambda Functions
        event_processor_lambda = _lambda.Function(
            self, "EventProcessor",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambdas"),
            handler="event_processor.handler",
            environment={
                "SLACK_SECRET_ARN": slack_secret_arn,
                "SLACK_EVENT_QUEUE_URL": queue.queue_url,
            }
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
            environment={
                "ANALYSIS_RESULTS_TABLE": analysis_results_table.table_name,
            },
        )

        # Get Slack verification token from Secrets Manager
        slack_secret = secretsmanager.Secret.from_secret_attributes(
            self,
            "SlackVerificationTokenSecret",
            secret_complete_arn=slack_secret_arn,
        )
        slack_secret.grant_read(event_processor_lambda)

        # Grant Lambda permissions
        queue.grant_send_messages(event_processor_lambda)  # For sending
        queue.grant_consume_messages(safety_analyzer_lambda)  # For consuming

        # Add SQS event source to safety_analyzer_lambda
        safety_analyzer_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(queue)
        )

        # Grant Lambda Permissions
        analysis_results_table.grant_read_write_data(safety_analyzer_lambda)

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