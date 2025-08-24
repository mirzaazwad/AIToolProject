PY=python
PIP=pip

.PHONY: setup test run fmt

setup:
	$(PY) -m venv .venv && . .venv/bin/activate && $(PIP) install -r requirements.txt

test:
	pytest --cov=. tests/ --cov-report=xml

run:
	$(PY) main.py "What is 12.5% of 243?"

sonar:
	sonar-scanner   -Dsonar.projectKey=AIToolProject   -Dsonar.sources=.   -Dsonar.host.url=http://localhost:4000   -Dsonar.login=$$SONAR_TOKEN

fmt:
	black .
