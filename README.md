# Slack Guardian

Slack Guardian is a project designed to manage and monitor Slack workspaces using AWS Lambda and AWS CDK. It uses OpenAI to analyze slack messages.
The architecture of the finished product can be seen [here](https://mermaid.live/edit#pako:eNqFVE1v4jAU_CuWD3sCRMJncliJAqVIhQYSVGlDDyZ5QNTERnbSLUX972s7ZhfSbnuJ4peZeZN5tk84YjFgF-84OexRMFpThESxKZd-SqJnVUFoEOoFemT8WRxIBE-oXlcAsUdDlmWExkJWfqJ5eFVEq-X9k5FQjPEL0LxE3hhJXUIDb_qEFBBovKZXNgaPPprSLSci50WUFxxKwbkSvAsCD3kPfqA1h3YohdCE5PCbHFH9rw2P5HvjY2gr3pS-sGconTxUPN_JRwoc3ZNsExNDe1Cs1SGW0kIi6TbZafIsHER5wui5NjpSkrHRjaHdfGLSqpgsE7i0aFUtjkID4iwCIVjF3EjhFwUUEj6T38kONG0c-gu__GCQY4UMeLLbAS-lb0OfbCE_ogEl6fGt-t-3etCg5nupPAmHe5JPvEBProROFHQJckJUlGoiEegH8gvZTeQQIxOVbnspnzMunS9BFKnZHXdhJcjbD8an5-Q_ndfUmOEJvFQmdgHwik2aiH0lNi_05z4K2CGJjJr3n4BX1r-E1SQzkqTfUewrij4E31Fa15SZbwgr6yqVMgC0ldtD0Rah9iPz34iIJxvgZ5r9FW1pDuZHWusrmh9KX1WSPs24hjPg0kosb5qTKq9xvocM1tiVrzFsiZz7Gq_pu4SSImf-kUbYlccdarjQZ26UEHkbZOfigVDsnvArdh270WnZTbvf7PZsp-10a_iI3brVbjecTq_Vs62O3e222v33Gn5jTCpYjabltJxev9PuN9uOY_fOTcZxIncidrckFbIJ6OWsvCH1Rakb_9Iqysf7Hyo6m3Y).

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

```
slack-guardian/
├── app.py                      # Main application file
├── package_lambdas.sh          # Script to package AWS Lambda functions
├── source.bat                  # Batch file for setting environment variables.
├── pytest.ini                  # Pytest configuration file
├── slack_guardian/             # CDK Source code for AWS infra
├── lambdas/                    # Directory containing Lambda functions
├── .coveragerc                 # Coverage configuration file
├── README.md                   # Project README file
├── cdk.json                    # AWS CDK configuration file
├── requirements-dev.txt        # Development dependencies
├── requirements.txt            # Project dependencies
├── .gitignore                  # Git ignore file
├── tests/                      # Directory containing tests
└── Makefile                    # Makefile for running tests and creating infrastructure
```

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.8+
- AWS CLI configured with the necessary permissions
- Node.js and npm (for AWS CDK)
- `make` program to run makefiles

## Installation

1. The CDK pipeline uses GitHub commits to trigger redeployments, so you need to fork this repository. After that, you need to clone your own fork:
   ```sh
   git clone https://github.com/<your-repo>/slack-guardian.git
   cd slack-guardian
   ```

2. Create a virtual environment and activate it:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Install the development dependencies:
   ```sh
   pip install -r requirements-dev.txt
   ```

5. Install the AWS CDK:
   ```sh
   npm install -g aws-cdk
   ```

## Configuration

1. Create a new app on `api.slack.com`.
2. Copy the Slack bot token to the AWS Secret Manager. Name it `slack-bot-token`.
3. Copy the Slack signing secret to the AWS Secret Manager. Name it `slack-signing-secret`.
4. Create your OpenAI secret key and copy it to the AWS Secret Manager. Name it `openai-secret-key`.
5. Configure your GitHub token and copy it to the AWS Secret Manager. Name it `github-token`.

## Usage

### Deployment

Every push to GitHub will deploy the app. To deploy it manually, use:
```
make deploy
```
Once deployed to the `/events` URL to your Slack project's `event-subscriptions` page.
For example, if your AWS API Gateway says that the `/prod` URL is `https://ucn3xaslm0.execute-api.us-east-1.amazonaws.com/prod`, then your `/events` URL is `https://ucn3xaslm0.execute-api.us-east-1.amazonaws.com/prod/events`.
If your Slack project id is `AXXXXXXXXXF`, then your `events-subscriptions` page is `https://api.slack.com/apps/AXXXXXXXXXF/event-subscriptions`. Set the `Request URL` field of the `event-subscriptions` page to the `/events` URL. 

### Running the Application

To install the application in your Slack channel,
go to your Slack Workspace, install the `slack-guardian` bot by typing `@slack-guardian`.

## Testing the code

To run unit tests, use:
```sh
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
