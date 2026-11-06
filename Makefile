.PHONY: up down train test lint clean

# Default subset parameter (empty means full dataset)
SUBSET ?=

up:
	k3d cluster create --config cluster/k3d.yaml || true
	kubectl apply -f k8s/seaweedfs.yaml
	docker build -t command-parser:latest .
	k3d image import command-parser:latest -c mycluster
	kubectl apply -f k8s/app.yaml

down:
	k3d cluster delete mycluster

train:
ifdef SUBSET
	python training/train.py --subset $(SUBSET)
else
	python training/train.py
endif

test:
	pytest tests/ -v

lint:
	flake8 service/ worker/ training/ tests/ --max-line-length=120 --ignore=E203,W503,E501

clean:
	rm -rf __pycache__ .pytest_cache
