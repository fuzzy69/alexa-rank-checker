.PHONY: tests

DIR := ${CURDIR}


help:
	@echo "clean - remove Python file artifacts"
	@echo "lint  - check style with flake8"
	@echo "tests - run unittests"
	@echo "setup - setup application"

setup:
	virtualenv -p python3 env
	. env/bin/activate && pip install -r requirements.txt

clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

unittest:
	python -m unittest discover -v

lint:
	flake8 --exclude .git,__pycache__,env,_ > _/lint.log