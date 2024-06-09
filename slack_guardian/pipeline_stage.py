from constructs import Construct
from aws_cdk import Stage
from slack_guardian.service_stack import SlackGuardianStack

class SlackGuardianPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = SlackGuardianStack(self, "SlackGuardianWebService")