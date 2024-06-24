import aws_cdk as core
import aws_cdk.assertions as assertions

from slack_guardian.pipeline_stack import SlackGuardianPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in slack_guardian/pipeline_stack.py
def test_pipeline_stack():
    app = core.App()
    stack = SlackGuardianPipelineStack(app, "SlackGuardianPipelineStack")
    template = assertions.Template.from_stack(stack)
