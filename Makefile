install:
	pip install .[dev]

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest -q

docker-build:
	docker build -t quant-finbert:dev .

docker-run:
	docker compose up --build
