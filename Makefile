PYTHON ?= python3
SOURCES := luoxia
# TESTS := tests
# TOOLS := tools
ROOT_DIR ?= $(shell git rev-parse --show-toplevel)

# Color
no_color = \033[0m
black = \033[0;30m
red = \033[0;31m
green = \033[0;32m
yellow = \033[0;33m
blue = \033[0;34m
purple = \033[0;35m
cyan = \033[0;36m
white = \033[0;37m

# Version
RELEASE_VERSION ?= $(shell git rev-parse --short HEAD)_$(shell date -u +%Y-%m-%dT%H:%M:%S%z)
GIT_BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
GIT_COMMIT ?= $(shell git rev-parse --verify HEAD)

.PHONY: help
help:
	@echo "Skyline API server development makefile"
	@echo
	@echo "Usage: make <TARGET>"
	@echo
	@echo "Target:"
	@echo "  git_config          Initialize git configuration."
	@echo "  clean               Clean up."
	@echo "  build               Build docker image."
	@echo "  init_venv           init venv."
	@echo "  install_dependence  install_ dependence"
	@echo "  run_api             run fastapi server."
	@echo "  run_streamlit       run streamlit server."
	@echo


.PHONY: git_config clean lint fmt build devbuild init_venv use_venv install_dependence run_api run_streamlit
user_name = $(shell git config --get user.name)
user_email = $(shell git config --get user.email)
commit_template = $(shell git config --get commit.template)
git_config:
ifeq ($(user_name),)
	@printf "$(cyan)\n"
	@read -p "Set your git user name: " user_name; \
    git config --local user.name $$user_name; \
    printf "$(green)User name was set.\n$(cyan)"
endif
ifeq ($(user_email),)
	@printf "$(cyan)\n"
	@read -p "Set your git email address: " user_email; \
    git config --local user.email $$user_email; \
    printf "$(green)User email address was set.\n$(no_color)"
endif
ifeq ($(commit_template),)
	@git config --local commit.template $(ROOT_DIR)/tools/git_config/commit_message.txt
endif
	@printf "$(green)Project git config was successfully set.\n$(no_color)"
	@printf "${yellow}You may need to run 'pip install git-review' install git review tools.\n\n${no_color}"


clean:
	rm -rf .venv dist htmlcov .coverage log test_results.html build .tox skyline_apiserver.egg-info AUTHORS ChangeLog storage

lint:
	# poetry run mypy --no-incremental $(SOURCES)
	# poetry run isort --check-only --diff $(SOURCES) $(TESTS) $(TOOLS)
	# poetry run black --check --diff --color $(SOURCES) $(TESTS) $(TOOLS)
	# poetry run flake8 $(SOURCES) $(TESTS) $(TOOLS)
	poetry run isort --check-only --diff $(SOURCES)
	poetry run black --check --diff --color $(SOURCES)
	poetry run flake8 $(SOURCES)

fmt:
	# poetry run isort $(SOURCES) $(TESTS) $(TOOLS)
	# poetry run black $(SOURCES) $(TESTS) $(TOOLS)
	# poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed `find $(SOURCES) -name '*.py'`
	poetry run isort $(SOURCES)
	poetry run black $(SOURCES)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed `find $(SOURCES) -name '*.py'`
BUILD_ENGINE ?= docker
BUILD_CONTEXT ?= .
DOCKER_FILE ?= container/Dockerfile
IMAGE ?= skyline
IMAGE_TAG ?= latest
ifeq ($(BUILD_ENGINE), docker)
    build_cmd = docker build
else ifeq ($(BUILD_ENGINE), buildah)
    build_cmd = buildah bud
else
    $(error Unsupported build engine $(BUILD_ENGINE))
endif
build: skyline_console/skyline_console.tar.gz skyline_console/commit_id
	$(build_cmd) --no-cache --pull --force-rm \
	  --build-arg GIT_CONSOLE_COMMIT=$(shell cat skyline_console/commit_id) \
	  --build-arg GIT_BRANCH=$(GIT_BRANCH) \
	  --build-arg GIT_COMMIT=$(GIT_COMMIT) \
	  --build-arg RELEASE_VERSION=$(RELEASE_VERSION) \
	  $(BUILD_ARGS) -f $(DOCKER_FILE) -t $(IMAGE):$(IMAGE_TAG) $(BUILD_CONTEXT)
devbuild: skyline_console/skyline_console.tar.gz skyline_console/commit_id
	$(build_cmd) \
	  --build-arg GIT_CONSOLE_COMMIT=$(shell cat skyline_console/commit_id) \
	  --build-arg GIT_BRANCH=devbuild \
	  --build-arg GIT_COMMIT=devbuild \
	  --build-arg RELEASE_VERSION=devbuild \
	  $(BUILD_ARGS) -f $(DOCKER_FILE) -t $(IMAGE):$(IMAGE_TAG) $(BUILD_CONTEXT)


init_venv:
	python -m venv .venv

init_venv:
	poetry env use .venv/bin/python

install_dependence:
	pip install -r requirements.txt

run_api:
	python main.python

run_streamlit: 
	streamlit run $(ROOT_DIR)/luoxia/streamlit_web/main.py --browser.serverAddress="0.0.0.0" \
	--server.enableCORS=True --browser.gatherUsageStats=False
