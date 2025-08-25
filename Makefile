PY=python
PIP=pip

.PHONY: setup install test run fmt sonar_local sonar_cloud clean


setup:
	$(PY) -m venv .venv && . .venv/bin/activate && $(PIP) install -r requirements.txt


install:
	$(PIP) install -r requirements.txt


test:
	pytest --cov=. tests/ --cov-report=xml


run:
	$(PY) main.py "What is 12.5% of 243?" -a gemini -v


sonar_local:
	@if [ -z "$$SONAR_TOKEN_LOCAL" ]; then \
		echo "❌ SONAR_TOKEN_LOCAL environment variable is required"; \
		echo "Export your token: export SONAR_TOKEN_LOCAL=your_token_here"; \
		exit 1; \
	fi
	sonar-scanner -Dsonar.projectKey=AIToolProject -Dsonar.sources=. -Dsonar.host.url=http://localhost:4000 -Dsonar.login=$$SONAR_TOKEN_LOCAL


sonar_cloud:
	@if [ -z "$$SONAR_TOKEN_CLOUD" ]; then \
		echo "❌ SONAR_TOKEN_CLOUD environment variable is required"; \
		echo "Export your token: export SONAR_TOKEN_CLOUD=your_token_here"; \
		exit 1; \
	fi
	sonar-scanner -Dsonar.projectKey=AIToolProject -Dsonar.sources=. -Dsonar.host.url=https://sonarcloud.io -Dsonar.login=$$SONAR_TOKEN_CLOUD

fmt:
	black .


clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -f coverage.xml
	rm -f .coverage
