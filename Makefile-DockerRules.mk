##
## Docker pattern targets. These pattern targets are Dockerfile and Planet python client agnostic
##
##     "make docker-build-<stage>" to build a stage locally.
##     "make docker-run-<stage>" to run a stage locally.
##     "make docker-publish-<stage>" to push a stage a docker repository.
##
## Options and arguments can be tailored for running each stage in the Dockerfile
## from make by setting the following in your makefile:
##     <stage>__DOCKER_RUN_OPTS=
##     <stage>__DOCKER_RUN_ARGS=
##

DOCKER_EXE:=docker
DOCKER_NAME:=$(if $(strip $(DOCKER_NAME)),$(strip $(DOCKER_NAME)),__unset_docker_name__)
DOCKER_FQNAME:=$(if $(strip $(DOCKER_FQNAME)),$(strip $(DOCKER_FQNAME)),__unset_docker_fqname__)
DOCKER_VERSION:=$(if $(strip $(DOCKER_VERSION)),$(strip $(DOCKER_VERSION)),__unset_docker_version__)
DOCKER_TAG_BASE:=$(if $(strip $(DOCKER_TAG_BASE)),$(strip $(DOCKER_TAG_BASE)),$(DOCKER_VERSION))


docker-build-%: ## Build and tag the docker stage '%'. The value of '%' is a wildcard, and will be expanded at runtime.
	$(DOCKER_EXE) build --target "$*" -t "$(DOCKER_NAME):$(DOCKER_TAG_BASE)-$*" .


docker-run-%: ## Execute the entrypoint for docker stage '%'. The value of '%' is a wildcard, and will be expanded at runtime.
docker-run-%: _docker_args=$($*__DOCKER_RUN_OPTS)
docker-run-%: _prog_args=$($*__DOCKER_RUN_ARGS)
docker-run-%: docker-build-%
	$(DOCKER_EXE) run --rm $(_docker_args) "$(DOCKER_NAME):$(DOCKER_TAG_BASE)-$*" $(_prog_args)


docker-fqtag-%: ## Tag the local docker image for the stage '%' with fully qualified name and tags suitable for publication to the the container registry. Some of the tags will omit the Dockerfile stage decoration.  WARNING: If you invoke docker-fqtag-% for multiple stages in the docker file, the undecorated tags WILL CLOBBER each other.  You should pay particular attention to how this interacts with the docker publishing targets.
docker-fqtag-%:  docker-build-%
	$(DOCKER_EXE) tag  "$(DOCKER_NAME):$(DOCKER_TAG_BASE)-$*" "$(DOCKER_FQNAME):$(DOCKER_TAG_BASE)-$*"
	$(DOCKER_EXE) tag  "$(DOCKER_NAME):$(DOCKER_TAG_BASE)-$*" "$(DOCKER_FQNAME):$(DOCKER_TAG_BASE)"


docker-publish-%: ## Publish the latest docker image for the stage '%' to the docker registry.  WARNING: If multiple stages are publised to the registry, docker tags that omit the stage decorator WILL clobber eachother.
docker-publish-%: docker-fqtag-%
	$(DOCKER_EXE) push "$(DOCKER_FQNAME):$(DOCKER_TAG_BASE)-$*"
	$(DOCKER_EXE) push "$(DOCKER_FQNAME):$(DOCKER_TAG_BASE)"


help:  ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | grep -v '^#' | sort | sed -e 's/:://' -e 's/://'|  awk -F' *## *' '{printf "%-25s : %s\n", $$1, $$2}'
