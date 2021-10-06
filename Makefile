sdist: clean test
	python3 setup.py sdist

publish: sdist
	twine upload --repository pypi dist/*

test:
	python3 test/uec.py

clean:
	rm -rf build/ dist/ *.egg-info/ *.lwp *.html

.PHONY: test
