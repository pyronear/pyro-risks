setup-dev:
	docker compose -f docker-compose.localstack.yml up -d --build
	docker compose exec localstack awslocal s3 mb s3://pyro-risk