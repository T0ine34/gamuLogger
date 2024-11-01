VERSION = 2.1.0


.PHONY: all

all: build install

ensure_env_exists:
	@if [ ! -d "env" ]; then \
		python3 -m venv env; \
	fi

ensure_testenv_exists:
	@if [ ! -d "testenv" ]; then \
		python3 -m venv testenv; \
	fi

install_build_deps: ensure_env_exists
	env/bin/pip install -r requirements-dev.txt

build: ensure_env_exists install_build_deps
	env/bin/feanor --debug -pv $(VERSION)

install: ensure_testenv_exists
	testenv/bin/pip install dist/*.whl --force-reinstall
