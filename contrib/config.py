from argparse import Namespace
from jinja2 import Environment, FileSystemLoader


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


def processConfig(args: Namespace) -> dict:
    config = dict()

    config['quiet'] = args.quiet
    config['root_dir'] = '/opt/terraform'
    config['work_dir'] = f"{config['root_dir']}/{args.type}"
    config['backend'] = processOptions(args.backend_options)
    config['template'] = {**processOptions(args.options), **{'region': args.region}}

    validateConfig(config)
    buildTerraformTemplate(config)

    return config


def processOptions(options: str) -> dict:
    opts_list = options.split(',')
    opts_dict = {}

    for opt in opts_list:
        k, v = opt.split('=')
        opts_dict[k] = v

    return opts_dict


def validateConfig(config: dict) -> None:
    if 'type' not in config['backend']:
        raise Exception("Missing 'type' in backend configuration!")
    if config['backend']['type'] == 's3':
        if 'bucket' not in config['backend']:
            raise Exception("Missing 'bucket' in backend configuration!")
        if 'state_name' not in config['backend']:
            raise Exception("Missing 'state_name' in backend configuration!")
        if 'region' not in config['backend']:
            raise Exception("Missing 'region' in backend configuration!")
    elif config['backend']['type'] == 'local':
        if 'path' not in config['backend']:
            raise Exception("Missing 'path' in backend configuration!")
    else:
        raise Exception(f"Unsupported backend: {config['backend']['type']}")

