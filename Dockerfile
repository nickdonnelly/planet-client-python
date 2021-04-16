##############################################################################
## Base image
##############################################################################
FROM python:3.9.4-alpine as base
RUN adduser -D -h /app appuser

##############################################################################
## Builder images
##############################################################################
#######################################
## Builder-1
#######################################
# Just our requirements in a builder image.  This image serves as a nice
# image to use as the python runtime environment during development with an IDE,
# since it has all our requrements, but not our code.
FROM base as builder-1
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv --system-site-packages  $VIRTUAL_ENV
WORKDIR /build

COPY requirements.txt ./requirements.txt
RUN python -m pip install  -r requirements.txt

#######################################
## Builder-2
#######################################
# Build just the CLI runtime for packaging up in a lean executable docker.
# The docker image is not built as distribution of the SDK for development
# at this time.
FROM builder-1 as builder-2
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /build

COPY LICENSE .
COPY README.rst .
COPY setup.cfg .
COPY setup.py .
COPY planet planet
COPY scripts scripts
# RUN python -m pip install -e .
RUN python -m pip install .

##############################################################################
## Development image
##############################################################################
# No such image at this time. Could be nice to provide an image with the
# Planet SDK installed ready for customer consumption.

#COPY CHANGES.txt .
#COPY docs docs
#COPY examples examples
#COPY tox.ini .

##############################################################################
## Runtime image
##############################################################################
FROM base as runtime
ENV VIRTUAL_ENV=/venv
COPY --from=builder-2 "$VIRTUAL_ENV" "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
USER appuser
ENTRYPOINT ["/venv/bin/planet"]

##############################################################################
## Unit test image
##############################################################################
# TODO: Test as close to production as possible:
#     - It would be better to test in the runtime rather than a builder container
#     - It would be nice to test as non-root or build user
FROM builder-2 as utest
# FROM runtime as utest
ENV CI=true

WORKDIR /build
RUN python -m pip install -e .[test]
COPY ./tests ./tests
# USER appuser
ENTRYPOINT [ "pytest", "tests" ]
