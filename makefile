
SOURCES = $(wildcard gamuLogger/*.py)
TESTS = $(wildcard tests/*.py)

TEMP_DIR = _build

VERSION = 0.1.0

WHEEL = gamulogger-$(VERSION)-py3-none-any.whl
ARCHIVE = gamulogger-$(VERSION).tar.gz

#env/bin/ if it exist, else env/Scripts/ if it exists, else nothing
PYTHON_FOLDER = $(shell if [ -d env/bin ]; then echo env/bin/; elif [ -d env/Scripts ]; then echo env/Scripts/; else echo ""; fi)


.PHONY: all clean install tests

all: dist/$(WHEEL) dist/$(ARCHIVE)


dist/$(WHEEL): $(SOURCES)
	mkdir -p $(TEMP_DIR)
	$(PYTHON_FOLDER)python build_package.py --outdir $(TEMP_DIR) --wheel --version $(VERSION)
	mkdir -p dist
	cp $(TEMP_DIR)/*.whl dist/
	rm -rf $(TEMP_DIR)

dist/$(ARCHIVE): $(SOURCES)
	mkdir -p $(TEMP_DIR)
	$(PYTHON_FOLDER)python build_package.py --outdir $(TEMP_DIR) --sdist --version $(VERSION)
	mkdir -p dist
	cp $(TEMP_DIR)/*.tar.gz dist/
	rm -rf $(TEMP_DIR)

install: dist/$(WHEEL)
	$(PYTHON_FOLDER)python -m pip install --force-reinstall dist/$(WHEEL)


tests: $(SOURCES) $(TESTS)
	-@$(PYTHON_FOLDER)coverage run --branch -m pytest --junitxml=test-report.xml tests
	@$(PYTHON_FOLDER)coverage html -d htmlcov --omit=env/*,tests/*,gamuLogger/__init__.py --title "gamuLogger Test Coverage"
	@$(PYTHON_FOLDER)coverage xml -o coverage.xml --omit=env/*,tests/*,gamuLogger/__init__.py
	@$(PYTHON_FOLDER)coverage report -m --omit=env/*,tests/*,gamuLogger/__init__.py --show-missing
	@rm -rf .coverage


clean:
	rm -rf build dist gamuLogger.egg-info
	rm -rf env
	rm -rf __pycache__
	rm -rf gamuLogger/__pycache__
	rm -rf tests/__pycache__
