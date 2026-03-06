Commands:

```
# Set IAM account for gcloud
gcloud iam service-accounts create gemini-cli-sa-rsamborski-rag --description="Isolated account for Gemini CLI - rsamborski-rag project"

gcloud projects add-iam-policy-binding rsamborski-rag --member="serviceAccount:gemini-cli-sa-rsamborski-rag@rsamborski-rag.iam.gserviceaccount.com" --role="roles/alloydb.admin" --role="roles/aiplatform.user" --role="roles/run.admin" --role="roles/bigquery.dataViewer" --role="roles/bigquery.jobUser"



# Copy the Dockerfile
cp sandbox.Dockerfile ~/.gemini/sandbox.Dockerfile
```


Add following to `.gemini/settings.json:`:
```
{
  "tools": {
    "sandbox": "docker"
  }
}
```

Start with:
```
# Export the necessary environment variables
export GITHUB_TOKEN="github_pat_..."
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/sa-key.json"
export CLOUDSDK_CORE_PROJECT="YOUR_PROJECT_ID"
export GEMINI_API_KEY="your-api-key"
export GEMINI_SANDBOX=docker
export BUILD_SANDBOX=1  # makes sure we build image first

# Launch the interactive Gemini CLI
# It will use the .gemini/sandbox.Dockerfile to build and spin up the isolated micro-environment
gemini
```


To fix issues when running in brew, built the image manually by following:

```
# Install buildx
brew install docker-buildx

mkdir -p ~/.docker/cli-plugins
ln -sfn $(brew --prefix)/opt/docker-buildx/bin/docker-buildx ~/.docker/cli-plugins/docker-buildx

docker buildx version

# 1. Get the base name the CLI looks for
export IMAGE_BASE_NAME="us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox"

# 2. Get your currently installed Gemini CLI version (e.g., 0.32.1)
export IMAGE_TAG=$(gemini --version)

# 3. Combine them
export IMAGE_NAME="${IMAGE_BASE_NAME}:${IMAGE_TAG}"

# 4. Build your custom sandbox image
docker build -t "${IMAGE_NAME}" -f sandbox.Dockerfile .
```

Then we can run without BUILD_SANDBOX=1:
```
unset BUILD_SANDBOX
gemini
```
