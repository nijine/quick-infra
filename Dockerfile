FROM python:3.11.1-slim

# apt automation for non-interactive environment
ENV DEBIAN_FRONTEND=noninteractive

# terraform install pre-requisite
RUN apt-get update && apt-get install -y gnupg software-properties-common

# terraform install
# install HashiCorp GPG key
RUN wget -O- https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor | \
    tee /usr/share/keyrings/hashicorp-archive-keyring.gpg

# verify GPG key
RUN gpg \
    --check-signatures \
    --no-default-keyring \
    --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    2>/dev/null | \
    grep $(curl https://apt.releases.hashicorp.com/gpg 2>/dev/null | gpg --show-keys - | head -n 2 | tail -n 1)

# add HashiCorp apt repository
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    tee /etc/apt/sources.list.d/hashicorp.list

# install tools
RUN apt update && apt install -y \
    awscli \
    terraform

WORKDIR /opt/terraform

ADD . ./

ENTRYPOINT ["python3", "-u", "entrypoint.py"]
CMD ["help"]
