#!/usr/bin/env python3

import argparse
import subprocess
import sys


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


def runCreate(args: argparse.Namespace) -> None:
    # parse options
    # verbosity - there's absolutely a better way to do this but this works for now
    quiet_init = args.quiet >= 1
    quiet_plan = args.quiet >= 2
    quiet_apply = args.quiet >= 3

    # terraform working dir
    infra_root = args.type

    # populate config
    # TODO: make this reference a config file or something (i.e. config.py)
    env_root = "/opt/terraform"
    root_dir = f"{env_root}/{infra_root}" 

    # run terraform init, workspace opts if not n/a, and plan/apply
    init_args = ["terraform", f"-chdir={root_dir}", "init"]

    runBaseCmd(init_args, quiet_init)

    # run plan
    plan_args = ["terraform", f"-chdir={root_dir}", "plan"]

    runBaseCmd(plan_args, quiet_plan)

    # run apply
    apply_args = ["terraform", f"-chdir={root_dir}", "apply", "-auto-approve"]

    runBaseCmd(apply_args, quiet_apply)


def runPreview(args: argparse.Namespace) -> None:
    # parse options
    quiet_init = args.quiet >= 1
    quiet_plan = args.quiet >= 2  # in case you just want to see that no errors occur

    # terraform working dir
    infra_root = args.type

    # populate config
    # TODO: make this reference a config file or something (i.e. config.py)
    env_root = "/opt/terraform"
    root_dir = f"{env_root}/{infra_root}" 

    # run terraform init, workspace opts if not n/a, and plan
    init_args = ["terraform", f"-chdir={root_dir}", "init"]

    runBaseCmd(init_args, quiet_init)

    # run plan
    plan_args = ["terraform", f"-chdir={root_dir}", "plan"]

    runBaseCmd(plan_args, quiet_plan)


def runDestroy(args: argparse.Namespace) -> None:
    # parse options
    quiet_init = args.quiet >= 1
    quiet_destroy = args.quiet >= 2

    infra_root = args.type

    # populate config
    # TODO: make this reference a config file or something (i.e. config.py)
    env_root = "/opt/terraform"
    root_dir = f"{env_root}/{infra_root}" 

    # run terraform init, workspace opts if not n/a, and plan/apply
    init_args = ["terraform", f"-chdir={root_dir}", "init"]

    runBaseCmd(init_args, quiet_init)

    # run destroy
    init_args = ["terraform", f"-chdir={root_dir}", "destroy", "-auto-approve"]

    runBaseCmd(init_args, quiet_destroy)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="The action to perform", choices=["create", "preview", "destroy", "list"])
    # maybe make the choices auto-poplate based on file dirs?
    parser.add_argument("type", help="The type of infra to create", choices=["site", "app"])
    parser.add_argument("-o", "--options", help="A comma-separated list of optional settings to use with --type")
    parser.add_argument("-q", "--quiet", help="Reduces output (hides the various terraform run stages i.e. init, plan, apply)", action="count", default=0)
    parser.add_argument("-b", "--bucket", help="An S3 bucket to use for remote state")
    parser.add_argument("-s", "--state-name", help="A custom name to use for the state file")
    parser.add_argument("-w", "--workspace", help="A custom workspace name")

    # TODO: Add some descriptors to the actions, as needed

    args = parser.parse_args()

    if args.action == "create":
        runCreate(args)
    elif args.action == "preview":
        runPreview(args)
    elif args.action == "destroy":
        runDestroy(args)


if __name__ in '__main__':
    main()
