sdist: clean
	python3 setup.py sdist

publish: sdist
	twine upload --repository pypi dist/*

clean:
	rm -rf build/ dist/ *.egg-info/
