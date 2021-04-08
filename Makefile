API_VERSION=$(shell sed -e 's/.*=//' -e 's/[^0-9a-zA-Z\._-]//g'  planet/api/__version__.py)

DOCKER_NAME:=planet
DOCKER_FQNAME:=planetlabs/$(DOCKER_NAME)
DOCKER_VERSION:=$(API_VERSION)$(if $(strip $(BUILD_NUM)),.$(strip $(BUILD_NUM)),)
# Decorate local docker builds to distinguish them from any official releases
DOCKER_TAG_DECORATOR=$(if $(CI_COMMIT_SHA),,--dev-$(USER_NAME))

runtime__DOCKER_RUN_OPTS=-ti
runtime__DOCKER_RUN_ARGS=--help


include build-tools/make/common-defs.mk
include build-tools/make/docker-defs.mk

default: help

include build-tools/make/common-rules.mk
include build-tools/make/docker-rules.mk
include build-tools/make/printenv-rules.mk

