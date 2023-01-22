#!/usr/bin/env python3

from contrib.config import processConfig
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


def runCreate(opts: dict) -> None:
    work_dir = opts.get('work_dir', '.')
    quiet = opts.get('quiet', -1)

    init_args = ["terraform", f"-chdir={work_dir}", "init"]
    plan_args = ["terraform", f"-chdir={work_dir}", "plan"]
    apply_args = ["terraform", f"-chdir={work_dir}", "apply", "-auto-approve"]

    # run init, plan, and apply
    runBaseCmd(init_args, quiet >= 1)
    runBaseCmd(plan_args, quiet >= 2)
    runBaseCmd(apply_args, quiet >= 3)


def runPreview(opts: dict) -> None:
    work_dir =  opts.get('work_dir', '.')
    quiet = opts.get('quiet', -1)

    init_args = ["terraform", f"-chdir={work_dir}", "init"]
    plan_args = ["terraform", f"-chdir={work_dir}", "plan"]

    # run init and plan
    runBaseCmd(init_args, quiet >= 1)
    runBaseCmd(plan_args, quiet >= 2)


def runDestroy(opts: dict) -> None:
    work_dir =  opts.get('work_dir', '.')
    quiet = opts.get('quiet', -1)

    init_args = ["terraform", f"-chdir={work_dir}", "init"]
    destroy_args = ["terraform", f"-chdir={work_dir}", "destroy", "-auto-approve"]

    # run init and destroy
    runBaseCmd(init_args, quiet >= 1)
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
