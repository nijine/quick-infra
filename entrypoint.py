#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
import argparse
import subprocess
import sys


ARG_DEFAULTS = {
    'backend': 'local',
    'region': 'us-east-1',
}

APP_DEFAULTS = {
    'site': {
        'domain_name': 'example.com',
    },
    'app': {
    },
}

BACKEND_DEFAULTS = {
    's3': {
        'bucket': 'my-terraform-bucket',
        'state_name': 'terraform',
        'bucket_region': 'us-east-1',
    },
    'local': {
        'path': '/state/terraform.tfstate',
    },
}


def runBaseCmd(cmd: list, quiet: bool=False) -> None:
    errs = []

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as t_proc:
        if not quiet:
            for line in t_proc.stdout:
                print(line.rstrip())

        for line in t_proc.stderr:
            errs.append(line.rstrip())

    if t_proc.returncode != 0:
        for line in errs:
            print(line)
        print(f"Issue running command: {' '.join(cmd)}")
        sys.exit(1)


def buildTerraformTemplate(config: dict, opts: dict) -> None:
    # open backend template
    environment = Environment(loader=FileSystemLoader(f"{config['root_dir']}/backends"))
    template = environment.get_template(f"{opts['backend_type']}.tf.template")

    # pre-render backend block
    backend_block = template.render(opts)

    # open main.tf.template
    environment = Environment(loader=FileSystemLoader(config['work_dir']))
    template = environment.get_template("main.tf.template")

    # replace vars with listed options
    opts['backend_configuration'] = backend_block
    content = template.render(opts)

    # write out main.tf file
    with open(f"{config['work_dir']}/main.tf", mode="w", encoding="utf-8") as t_file:
        t_file.write(content)


# NOTE: see if we can clean up this structure a little
def processConfig(args: argparse.Namespace) -> dict:
    config = {}

    # verbosity
    config['quiet'] = args.quiet

    # terraform working dir
    infra_root = args.type

    config['root_dir'] = f"/opt/terraform"
    config['work_dir'] = f"{config['root_dir']}/{args.type}"

    # populate terraform template
    template_opts = processOptions(args.options)

    # pre-process options with defaults
    template_opts = {**APP_DEFAULTS[args.type], **template_opts}

    backend = args.backend or ARG_DEFAULTS['backend']
    region = args.region or ARG_DEFAULTS['region']
    backend_opts = BACKEND_DEFAULTS[backend]
    backend_opts['backend_type'] = backend
    backend_opts['region'] = region

    # add backend options
    template_opts = {**template_opts, **backend_opts}

    buildTerraformTemplate(config, template_opts)

    config['template'] = template_opts

    return config


def processOptions(options: str) -> dict:
    if options == "":
        return {}

    opts_list = options.split(',')
    opts_dict = {}

    for opt in opts_list:
        k, v = opt.split('=')
        opts_dict[k] = v

    return opts_dict


def runCreate(opts: dict) -> None:
    work_dir = opts.get('work_dir', '.')
    quiet = opts.get('quiet', -1)

    # run terraform init, workspace opts if not n/a, and plan/apply
    init_args = ["terraform", f"-chdir={work_dir}", "init"]

    runBaseCmd(init_args, quiet >= 1)

    # run plan
    plan_args = ["terraform", f"-chdir={work_dir}", "plan"]

    runBaseCmd(plan_args, quiet >= 2)

    # run apply
    apply_args = ["terraform", f"-chdir={work_dir}", "apply", "-auto-approve"]

    runBaseCmd(apply_args, quiet >= 3)


def runPreview(opts: dict) -> None:
    work_dir =  opts.get('work_dir', '.')
    quiet = opts.get('quiet', -1)

    # run terraform init, workspace opts if not n/a, and plan
    init_args = ["terraform", f"-chdir={work_dir}", "init"]

    runBaseCmd(init_args, quiet >= 1)

    # run plan
    plan_args = ["terraform", f"-chdir={work_dir}", "plan"]

    runBaseCmd(plan_args, quiet >= 2)


def runDestroy(opts: dict) -> None:
    work_dir =  opts.get('work_dir', '.')
    quiet = opts.get('quiet', -1)

    # run terraform init, workspace opts if not n/a, and plan/apply
    init_args = ["terraform", f"-chdir={work_dir}", "init"]

    runBaseCmd(init_args, quiet >= 1)

    # run destroy
    destroy_args = ["terraform", f"-chdir={work_dir}", "destroy", "-auto-approve"]

    runBaseCmd(destroy_args, quiet >= 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="The action to perform", choices=["create", "preview", "destroy", "debug"])
    parser.add_argument("type", help="The type of infra to create", choices=["site"])
    parser.add_argument("-o", "--options", help="A comma-separated list of optional settings to use with --type", default="")
    parser.add_argument("-q", "--quiet", help="Reduces output (hides the various terraform run stages i.e. init, plan, apply)", action="count", default=0)
    parser.add_argument("-r", "--region", help="The region to use for the provider")
    parser.add_argument("-e", "--backend", help="The type of backend to use for terraform state", choices=["local", "s3"])
    parser.add_argument("-p", "--path", help="The path to use when using a local state backend")
    parser.add_argument("-b", "--bucket", help="An S3 bucket to use for remote state")
    parser.add_argument("--bucket-region", help="The S3 bucket region to use for the remote state")
    parser.add_argument("-s", "--state-name", help="A custom name to use for the state file")
    # TODO: implement
    # parser.add_argument("-w", "--workspace", help="A custom workspace name")

    args = parser.parse_args()

    # process config and build terraform files
    config = processConfig(args)

    if args.action == "debug":
        print(f"Config: {config}")
        print("main.tf:")
        with open(f"{config['work_dir']}/main.tf", 'r') as t_file:
            for line in t_file.readlines():
                print(line.rstrip())
        exit(0)

    elif args.action == "create":
        runCreate(config)
    elif args.action == "preview":
        runPreview(config)
    elif args.action == "destroy":
        runDestroy(config)


if __name__ in '__main__':
    main()
