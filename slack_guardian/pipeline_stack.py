from aws_cdk import (
    Stack,
)
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from slack_guardian.pipeline_stage import SlackGuardianPipelineStage


class SlackGuardianPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipeline =  CodePipeline(
            self, "Pipeline",
            pipeline_name="SlackGuardianPipeline",
            synth=ShellStep("Synth",
                input=CodePipelineSource.git_hub("aldian/slack-guardian", "main"),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth"
                ]
            )
        )

        deploy = SlackGuardianPipelineStage(self, "Deploy")
        deploy_stage = pipeline.add_stage(deploy)