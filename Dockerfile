FROM python:3.11.1-slim

# apt automation for non-interactive environment
ENV DEBIAN_FRONTEND=noninteractive

# terraform install pre-requisites
RUN apt-get update && apt-get install -y gnupg software-properties-common wget

# install HashiCorp GPG key
RUN wget -O- https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor | \
    tee /usr/share/keyrings/hashicorp-archive-keyring.gpg

# add HashiCorp apt repository
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    tee /etc/apt/sources.list.d/hashicorp.list

# install tools
RUN apt update && apt install -y \
    awscli \
    terraform

# set base dir for cmds, etc
WORKDIR /opt/terraform

# add files
ADD . ./

# default entrypoint / cmd
ENTRYPOINT ["python3", "-u", "entrypoint.py"]
CMD ["help"]
