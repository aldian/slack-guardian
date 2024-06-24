test:
	coverage run -m pytest -s
	coverage report -m

deploy:
	cdk deploy

destroy:
	cdk destroy
