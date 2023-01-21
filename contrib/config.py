from argparse import Namespace
from dataclasses import dataclass
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

@dataclass
class LocalBackendConfig:
    template_path: str = 'backends/local.tf.template'
    state_path: str = '/state/terraform.tfstate'


@dataclass
class S3BackendConfig:
    template_path: str = 'backends/s3.tf.template'
    bucket: str
    state_name: str
    region: str


@dataclass
class SiteConfig:
    domain_name: str = 'example.com'


class Config:
    def __init__(self, backend_config, type_config):
        self.backend_config = backend_config
        self.type_config = type_config


def buildTerraformTemplate(config: dict) -> None:
    template_opts = config['template']
    backend_opts = config['backend']

    # open backend template
    environment = Environment(loader=FileSystemLoader(f"{config['root_dir']}/backends"))
    template = environment.get_template(f"{backend_opts['type']}.tf.template")

    # pre-render backend block
    backend_block = template.render(backend_opts)

    # open main.tf.template
    environment = Environment(loader=FileSystemLoader(config['work_dir']))
    template = environment.get_template("main.tf.template")

    # replace vars with listed options
    template_opts['backend_configuration'] = backend_block
    content = template.render(template_opts)

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

    # populate terraform template, including defaults
    template_opts = processOptions(args.app_options)
    template_opts = {**APP_DEFAULTS[args.type], **template_opts}

    # populate backend options, including defaults
    backend_opts = processOptions(args.backend_options)
    backend_opts.setdefault('type', ARG_DEFAULTS['backend'])
    backend_opts = {**BACKEND_DEFAULTS[backend_opts['type']], **backend_opts}

    config['backend'] = backend_opts
    config['template'] = template_opts

    buildTerraformTemplate(config)

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


