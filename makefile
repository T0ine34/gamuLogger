
SOURCES = $(wildcard gamuLogger/*.py)
TESTS = $(wildcard tests/*.py)

TEMP_DIR = build

VERSION = 0.1.0

.PHONY: all clean install tests wheel archive

all: install tests

env:
	python3.12 -m venv env
	env/bin/pip install --upgrade pip pytest setuptools wheel build

wheel: $(SOURCES) env
	mkdir -p $(TEMP_DIR)
	env/bin/python build_package.py --outdir $(TEMP_DIR) --wheel --version $(VERSION)
	mkdir -p dist
	cp $(TEMP_DIR)/*.whl dist/
	rm -rf $(TEMP_DIR)

archive: $(SOURCES) env
	mkdir -p $(TEMP_DIR)
	env/bin/python build_package.py --outdir $(TEMP_DIR) --sdist --version $(VERSION)
	mkdir -p dist
	cp $(TEMP_DIR)/*.tar.gz dist/
	rm -rf $(TEMP_DIR)

install: wheel env
	env/bin/python -m pip install --upgrade $(wildcard dist/*.whl)


tests: $(TESTS) install env
	env/bin/python -m pytest tests

clean:
	rm -rf build dist gamuLogger.egg-info
	rm -rf env
	rm -rf __pycache__
	rm -rf gamuLogger/__pycache__
	rm -rf tests/__pycache__
