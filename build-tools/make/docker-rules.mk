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

docker-info: ## Print information about the docker build
	@echo "Docker name                   : $(DOCKER_NAME)"
	@echo "Docker FQ name                : $(DOCKER_FQNAME)"
	@echo "Docker tag base               : $(DOCKER_TAG_BASE)"
	@echo "Docker tag version            : $(DOCKER_VERSION)"


info:: docker-info

.PHONY:: docker-info


