from argparse import Namespace
from jinja2 import Environment, FileSystemLoader


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
def processConfig(args: Namespace) -> dict:
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


