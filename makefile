
SOURCES = $(wildcard gamuLogger/*.py)
TESTS = $(wildcard tests/*.py)

TEMP_DIR = build

VERSION = 0.1.0

WHEEL = gamulogger-$(VERSION)-py3-none-any.whl
ARCHIVE = gamulogger-$(VERSION).tar.gz

#env/bin/ if it exist, else env/Scripts/ if it exists, else nothing
PYTHON_FOLDER = $(shell if [ -d env/bin ]; then echo env/bin/; elif [ -d env/Scripts ]; then echo env/Scripts/; else echo ""; fi)


.PHONY: all clean install tests

all: dist/$(WHEEL) dist/$(ARCHIVE)

env:
	python3.12 -m venv env
	$(PYTHON_FOLDER)pip install --upgrade pytest setuptools wheel build

dist/$(WHEEL): $(SOURCES) env
	mkdir -p $(TEMP_DIR)
	$(PYTHON_FOLDER)python build_package.py --outdir $(TEMP_DIR) --wheel --version $(VERSION)
	mkdir -p dist
	cp $(TEMP_DIR)/*.whl dist/
	rm -rf $(TEMP_DIR)

dist/$(ARCHIVE): $(SOURCES) env
	mkdir -p $(TEMP_DIR)
	$(PYTHON_FOLDER)python build_package.py --outdir $(TEMP_DIR) --sdist --version $(VERSION)
	mkdir -p dist
	cp $(TEMP_DIR)/*.tar.gz dist/
	rm -rf $(TEMP_DIR)

install: dist/$(WHEEL) env
	$(PYTHON_FOLDER)python -m pip install --force-reinstall dist/$(WHEEL)


test-report.xml: $(SOURCES) $(TESTS) env
	$(PYTHON_FOLDER)python -m pytest --junitxml=test-report.xml tests


tests: test-report.xml

clean:
	rm -rf build dist gamuLogger.egg-info
	rm -rf env
	rm -rf __pycache__
	rm -rf gamuLogger/__pycache__
	rm -rf tests/__pycache__
