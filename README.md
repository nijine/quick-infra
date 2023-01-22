# quick-infra
Docker/Terraform-based tool for quickly standing up ad-hoc cloud infrastructure for testing, CI, prototyping, etc.

## Purpose
The purpose of this tool is to encapsulate the terraform cli and any necessary tools or relevant config in a dockerized environment, in order to make it easy to perform repeated tasks, typically in a CI environment. Can also be used locally, typically with a run script or alias to shortcut having to type out `docker run -it --rm ...`.

## Basic Usage
```
# clone the repo and build the image
git clone git@github.com:nijine/quick-infra.git
cd quick-infra
docker build -t qinfra .  # or whatever image tag works for you

# run quick-infra using the specified image tag
# ...using a config file located in ~/.aws and a local state file
docker run -it --rm -v ~/.aws:/root/.aws -v $(pwd)/state:/state qinfra <action> <template> <options>

# i.e.
docker run -it ... qinfra create site domain_name=example.com,some_other_option=some-value.here

# ...or using env vars and remote state
docker run -it --rm -e AWS_REGION=$AWS_REGION -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY qinfra create site domain_name=example.com -b type=s3,bucket=my-bucket-name,state_name=my-state-name-prefix,region=us-east-1

# when you're done with your infra
docker run ... qinfra destroy site domain_name=example.com ...

# if you just want to get a preview of what terraform will do
docker run ... qinfra preview site domain_name=example.com ...

# if you need to debug your configuration or generated templates
docker run ... qinfra debug site domain_name=example.com ...
```

You can of course omit `-it` from `docker run` if this is in a script or other automated environment (CI, etc).

## Basic tool workflow
This tool does the following when run:

* Looks for a folder with the same name as your `type` argument, containing `main.tf.template`
* Processes the given arguments or configuration and turns your `main.tf.template` into a `main.tf` file with all the parameters filled in
* Runs `terraform init` inside the same folder mentioned above, using the `-chdir` argument to `terraform`
* Runs whichever other terraform commands are relevant to the action you selected, i.e. `terraform plan` for `preview`, `... plan` and `... apply` for `create`, etc.

## Customization
There are many ways to customize how the tool behaves, how to pass configuration in, etc. The main thing to customize will be the kind of infrastructure templates that exist in the root directory.

`site` is an example of how to assemble a given template.
* Place the basic building blocks required in a main.tf.template file in a named folder, i.e. `my-app`
* Anything that you want to make configurable can be defined using a python jinja-style variable declaration, i.e. `{{ my_variable }}`
* Build the docker image after adding your custom files to the appropriate directories
* Run it: `docker run ... <your-image-tag> create my-app my_variable=some-value ...`
