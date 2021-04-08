help:  ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | grep -v '^#' | sort | sed -e 's/:://' -e 's/://'|  awk -F' *## *' '{printf "%-25s : %s\n", $$1, $$2}'


info:: ## Print build information
	@echo "Current user                  : $(USER_NAME)"
	@echo "Git branch slug               : $(GIT_BRANCH_SLUG)"
	@echo "Git commit sha                : $(GIT_SHA)"
	@echo "Git commit sha (short)        : $(GIT_SHA_SHORT)"
	@echo "Git commit sha (long)         : $(GIT_SHA_LONG)"
	@echo "Timestamp                     : $(TIMESTAMP)"


clean:: ## Run all clean targets


.PHONY:: help
.PHONY:: info
.PHONY:: clean
