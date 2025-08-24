PY=python
PIP=pip

.PHONY: setup install test run fmt sonar clean


setup:
	$(PY) -m venv .venv && . .venv/bin/activate && $(PIP) install -r requirements.txt


install:
	$(PIP) install -r requirements.txt


test:
	pytest --cov=. tests/ --cov-report=xml


run:
	$(PY) main.py "What is 12.5% of 243?" -a gemini -v


sonar:
	@if [ -z "$$SONAR_TOKEN" ]; then \
		echo "❌ SONAR_TOKEN environment variable is required"; \
		echo "Export your token: export SONAR_TOKEN=your_token_here"; \
		exit 1; \
	fi
	sonar-scanner -Dsonar.projectKey=AIToolProject -Dsonar.sources=. -Dsonar.host.url=https://sonarcloud.io -Dsonar.login=$$SONAR_TOKEN


fmt:
	black .


clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -f coverage.xml
	rm -f .coverage
