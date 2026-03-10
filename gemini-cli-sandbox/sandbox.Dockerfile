# Start from the official Gemini CLI sandbox image with proper version
ARG GEMINI_CLI_VERSION=0.32.1
FROM us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox:${GEMINI_CLI_VERSION}
#FROM gemini-cli-sandbox

# Switch to root to install system dependencies (gcloud)
USER root

# Install Google Cloud SDK, Git, and prerequisites
RUN apt-get update && apt-get install -y curl apt-transport-https ca-certificates gnupg git && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-cli

# Install Terraform
RUN apt-get update && apt-get install -y wget lsb-release && \
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform

# Install vim
RUN apt-get install -y vim

# Switch back to the non-root user (the official sandbox image uses 'node' as the default user)
USER node
WORKDIR /workspace

RUN git config --global credential.helper '!f() { echo "username=x-access-token"; echo "password=$GITHUB_TOKEN"; }; f'
