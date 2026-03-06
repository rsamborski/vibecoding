# Start from the official Gemini CLI sandbox image
FROM us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox:0.32.1

# Switch to root to install system dependencies (gcloud)
USER root

# Install Google Cloud SDK, Git, and prerequisites
RUN apt-get update && apt-get install -y curl apt-transport-https ca-certificates gnupg git && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-cli

# Switch back to the non-root user (the official sandbox image uses 'node' as the default user)
USER node
WORKDIR /workspace

# Configure Git to use the injected GitHub PAT
RUN git config --global url."https://api:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
