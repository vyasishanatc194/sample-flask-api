build:
	export GCP_KEY_PATH=$(shell pwd)/project_secrets/form_builder_google_service_account.json && docker-compose build

up-i:
	export GCP_KEY_PATH=$(shell pwd)/project_secrets/form_builder_google_service_account.json && docker-compose up

up:
	export GCP_KEY_PATH=$(shell pwd)/project_secrets/form_builder_google_service_account.json && docker-compose up -d

start:
	docker-compose stop

stop:
	docker-compose stop

remove:
	docker container rm -f npi_directory_api

restart:
	docker-compose restart

shell:
	docker exec -ti npi_directory_api bash

copy_repo:
	docker cp npi_directory_api npi_directory_api:/app

inspect_volume:
	docker volume inspect data_volume
