Commands:

```
# Set IAM account for gcloud
gcloud iam service-accounts create gemini-cli-sa-rsamborski-rag --description="Isolated account for Gemini CLI - rsamborski-rag project"

gcloud projects add-iam-policy-binding rsamborski-rag --member="serviceAccount:gemini-cli-sa-rsamborski-rag@rsamborski-rag.iam.gserviceaccount.com" --role="roles/alloydb.admin" --role="roles/aiplatform.user" --role="roles/run.admin" --role="roles/bigquery.dataViewer" --role="roles/bigquery.jobUser"

# Copy the Dockerfile
cp sandbox.Dockerfile .gemini/sandbox.Dockerfile
```

Start with:
```
# Export the necessary environment variables
export GITHUB_TOKEN="github_pat_..."
export GEMINI_API_KEY="your-api-key"
export CLOUDSDK_CORE_PROJECT="YOUR_PROJECT_ID"
export GEMINI_SANDBOX=docker

# We keep the ENV variables for our dynamic credentials
export SANDBOX_FLAGS="\
-e GITHUB_TOKEN=${GITHUB_TOKEN} \
-e CLOUDSDK_CORE_PROJECT=${CLOUDSDK_CORE_PROJECT} \
-e CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE=$(pwd)/sa-key.json"

# Launch the interactive Gemini CLI
# It will use the .gemini/sandbox.Dockerfile to build and spin up the isolated micro-environment
BUILD_SANDBOX=1 gemini
```


To fix issues when running in brew, built the image manually by following:

```
# Install dependencie
brew install docker colima docker-buildx

# Configure docker-buildx
mkdir -p ~/.docker/cli-plugins
ln -sfn $(brew --prefix)/opt/docker-buildx/bin/docker-buildx ~/.docker/cli-plugins/docker-buildx

# Start colima service
brew services start colima

# Update DOCKER_HOST (you might want to add this line to .bash_profile):
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"

# Get the base name the CLI looks for
export IMAGE_BASE_NAME="us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox"

# Get your currently installed Gemini CLI version (e.g., 0.32.1)
export IMAGE_TAG=$(gemini --version)

# Combine them
export IMAGE_NAME="${IMAGE_BASE_NAME}:${IMAGE_TAG}"

# Build your custom sandbox image
docker build -t "${IMAGE_NAME}" -f sandbox.Dockerfile .
```

Then we can run without BUILD_SANDBOX=1:
```
gemini
```
