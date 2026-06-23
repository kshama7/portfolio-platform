SHELL := /bin/bash
.DEFAULT_GOAL := help
APP_VERSION ?= 0.1.0
REGISTRY    ?= ghcr.io/kshama7
API_IMAGE   := $(REGISTRY)/portfolio-platform-api:$(APP_VERSION)
WEB_IMAGE   := $(REGISTRY)/portfolio-platform-web:$(APP_VERSION)

.PHONY: help
help: ## show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Local dev
.PHONY: api-dev
api-dev: ## run api with reload
	cd api && PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload --port 8000

.PHONY: web-dev
web-dev: ## run web dev server
	cd web && NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev

.PHONY: up
up: ## start full stack with docker-compose
	APP_VERSION=$(APP_VERSION) docker compose up --build

.PHONY: down
down: ## stop docker-compose stack
	docker compose down -v

##@ Quality
.PHONY: test
test: ## run python tests
	cd api && PYTHONPATH=. .venv/bin/pytest -q

.PHONY: lint
lint: ## lint python + ts
	cd api && .venv/bin/ruff check app tests
	cd web && npm run lint

.PHONY: typecheck
typecheck: ## typecheck ts
	cd web && ./node_modules/.bin/tsc --noEmit

##@ Build & push
.PHONY: build
build: build-api build-web ## build both images

.PHONY: build-api
build-api:
	docker build --build-arg APP_VERSION=$(APP_VERSION) -t $(API_IMAGE) api

.PHONY: build-web
build-web:
	docker build -t $(WEB_IMAGE) web

.PHONY: push
push: ## push both images
	docker push $(API_IMAGE)
	docker push $(WEB_IMAGE)

##@ Deploy
.PHONY: helm-lint
helm-lint: ## lint helm chart
	helm lint infra/helm/portfolio-platform

.PHONY: helm-template
helm-template: ## render helm chart
	helm template portfolio-platform infra/helm/portfolio-platform

.PHONY: fly-deploy-api
fly-deploy-api: ## deploy api to fly.io
	cd infra/fly && fly deploy -c api.fly.toml

.PHONY: fly-deploy-web
fly-deploy-web: ## deploy web to fly.io
	cd infra/fly && fly deploy -c web.fly.toml

##@ Load & chaos
.PHONY: load-smoke
load-smoke: ## k6 smoke test against local
	k6 run tests/load/k6-smoke.js -e BASE_URL=http://localhost:8000

.PHONY: load-stress
load-stress: ## k6 stress test
	k6 run tests/load/k6-stress.js -e BASE_URL=http://localhost:8000
