DOCKER_EXE:=docker
DOCKER_NAME:=$(if $(strip $(DOCKER_NAME)),$(strip $(DOCKER_NAME)),__unset_docker_name__)
DOCKER_FQNAME:=$(if $(strip $(DOCKER_FQNAME)),$(strip $(DOCKER_FQNAME)),__unset_docker_fqname__)
DOCKER_VERSION:=$(if $(strip $(DOCKER_VERSION)),$(strip $(DOCKER_VERSION)),__unset_docker_version__)
DOCKER_TAG_BASE:=$(if $(strip $(DOCKER_TAG_BASE)),$(strip $(DOCKER_TAG_BASE)),$(DOCKER_VERSION))$(DOCKER_TAG_DECORATOR)

