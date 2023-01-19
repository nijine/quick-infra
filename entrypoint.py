#!/usr/bin/env python3

import argparse
import subprocess
import sys
from threading import Thread


def runBaseCmd(cmd: list, opts: dict={}) -> None:
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as t_proc:
        for line in t_proc.stdout:
            print(line.rstrip())

    if t_proc.returncode != 0:
        print("Issue running {cmd}")
        sys.exit(1)


def runCreate(args: argparse.Namespace) -> None:
    # parse options
    # verbosity - there's absolutely a better way to do this but this works for now
    quiet = args.quiet

    # terraform working dir
    infra_root = args.type

    # populate config
    # TODO: make this reference a config file or something (i.e. config.py)
    env_root = "/opt/terraform"
    root_dir = f"{env_root}/{infra_root}" 

    # run terraform init, workspace opts if not n/a, and plan/apply
    init_args = ["terraform", f"-chdir={root_dir}", "init"]

    runBaseCmd(init_args)

    # run plan
    plan_args = ["terraform", f"-chdir={root_dir}", "plan"]

    runBaseCmd(plan_args)

    # run apply
    apply_args = ["terraform", f"-chdir={root_dir}", "apply", "-auto-approve"]

    runBaseCmd(apply_args)


def runPreview(args: argparse.Namespace) -> None:
    # parse options
    quiet = args.quiet

    # terraform working dir
    infra_root = args.type

    # populate config
    # TODO: make this reference a config file or something (i.e. config.py)
    env_root = "/opt/terraform"
    root_dir = f"{env_root}/{infra_root}" 

    # run terraform init, workspace opts if not n/a, and plan
    init_args = ["terraform", f"-chdir={root_dir}", "init"]

    runBaseCmd(init_args)

    # run plan
    plan_args = ["terraform", f"-chdir={root_dir}", "plan"]

    runBaseCmd(plan_args)


def runDestroy(args: argparse.Namespace) -> None:
    # parse options
    infra_root = args.type

    # populate config
    # TODO: make this reference a config file or something (i.e. config.py)
    env_root = "/opt/terraform"
    root_dir = f"{env_root}/{infra_root}" 

    # run terraform init, workspace opts if not n/a, and plan/apply
    init_args = ["terraform", f"-chdir={root_dir}", "init"]

    result = subprocess.run(init_args, capture_output=True)

    if result.returncode != 0:
        print(result.stdout, '\n', result.stderr)
        raise Exception("Terraform init failed during runDestroy!")

    # run destroy
    init_args = ["terraform", f"-chdir={root_dir}", "destroy", "-auto-approve"]

    result = subprocess.run(init_args, capture_output=True)

    if result.returncode != 0:
        print(result.stdout, '\n', result.stderr)
        raise Exception("Terraform init failed during runDestroy!")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="The action to perform", choices=["create", "preview", "destroy", "list"])
    # maybe make the choices auto-poplate based on file dirs?
    parser.add_argument("type", help="The type of infra to create", choices=["site", "app"])
    parser.add_argument("-o", "--options", help="A comma-separated list of optional settings to use with --type")
    parser.add_argument("-q", "--quiet", help="Reduce output to errors only (-q) or no output (-qq)", action="count", default=0)
    parser.add_argument("-b", "--bucket", help="An S3 bucket to use for remote state")
    parser.add_argument("-s", "--state-name", help="A custom name to use for the state file")
    parser.add_argument("-w", "--workspace", help="A custom workspace name")

    # TODO: Add some descriptors to the actions, if possible

    args = parser.parse_args()

    if args.action == "create":
        runCreate(args)
    elif args.action == "preview":
        runPreview(args)
    elif args.action == "destroy":
        runDestroy(args)


if __name__ in '__main__':
    main()
