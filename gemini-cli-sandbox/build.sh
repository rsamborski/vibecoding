#!/bin/bash

# Update DOCKER_HOST (you might want to add this line to .bash_profile):
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"

# Get the base name the CLI looks for
export IMAGE_BASE_NAME="us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox"

# Get your currently installed Gemini CLI version (e.g., 0.32.1)
export GEMINI_CLI_VERSION=$(gemini --version)

# Combine them
export IMAGE_NAME="${IMAGE_BASE_NAME}:${GEMINI_CLI_VERSION}"

# Build your custom sandbox image
docker build -t "${IMAGE_NAME}" --build-arg GEMINI_CLI_VERSION=$GEMINI_CLI_VERSION -f sandbox.Dockerfile .
