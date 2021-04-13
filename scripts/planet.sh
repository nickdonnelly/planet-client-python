#!/bin/bash
# Copyright 2020 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

PLANET_SDK_DOCKER_IMAGE=planetlabs/planet
PLANET_SDK_DOCKER_TAG=2.0.0

# TODO:
#     - Need to intercept and mangle CLI options that deal with file IO.
#       We need to bind mount into the docker, and adjust args to reflect
#       the bind mount paths
exec docker run --rm -ti "${PLANET_SDK_DOCKER_IMAGE}:${PLANET_SDK_DOCKER_TAG}" "$@"
