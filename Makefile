test:
	coverage run -m pytest
	coverage report -m

deploy:
	cdk deploy

destroy:
	cdk destroy
