clean:
	python dev/clean.py

deps:
	pip install -r requirements.txt --upgrade

deps-dev:
	pip install -r dev/requirements.txt --upgrade

deploy: clean docs-deploy pypi
	git push --tags
	twine upload -r pypi dist/*
	python dev/clean.py

docs-deploy:
	mkdocs build --clean
	python dev/move.py

pypi: clean
	python setup.py sdist bdist_wheel

pypi-test:
	python setup.py sdist upload -r pypitest

register:
	python setup.py register -r pypi

register-test:
	python setup.py register -r pypitest

test: clean
	tox