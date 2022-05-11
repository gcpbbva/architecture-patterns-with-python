test:
	pytest -vv --capture=tee-sys

watch-tests:
	ls *.py | entr pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')
