import os

from configparser import ConfigParser


ARG_MAP = {
            "AWS_OKTA_USER": "--user",
            "AWS_OKTA_PASS": "--pass",
            "AWS_OKTA_ORGANIZATION": "--organization",
            "AWS_OKTA_APPLICATION": "--application",
            "AWS_OKTA_ROLE": "--role",
            "AWS_OKTA_DURATION": "--duration",
            "AWS_OKTA_SILENT": "--silent"
        }


def exits(name=None):
    profile_config = get_profile_config()

    if name in profile_config.sections():
        print("Profile [{}] already exists.".format(name))

        return True

    return False


def add(name=None, args=None, options=None):
    profile_config = get_profile_config()

    if options["--nt"]:
        command = ["aws-okta-processor.cmd"]
    else:
        command = ["aws-okta-processor"]

    command.append("token get")

    for arg in args:
        if args[arg] is True:
            command.append(ARG_MAP[arg])
            continue

        if args[arg] is not None:
            command.append(
                "{} {}".format(ARG_MAP[arg], args[arg])
            )

    command.append("--key {}".format(name))

    profile_config[name] = {}
    profile_config[name]["credential_process"] = " ".join(command)

    save_profile_config(profile_config)


def delete(name=None):
    profile_config = get_profile_config()

    if name in profile_config.sections():
        profile_config.remove_section(name)
        save_profile_config(profile_config)
        print("Profile [{}] deleted.".format(name))


def get_profile_config_path():
    home_directory = os.path.expanduser("~")
    aws_path = os.path.join(
        home_directory,
        ".aws"
    )

    if not os.path.isdir(aws_path):
        os.makedirs(aws_path)

    return os.path.join(
        aws_path,
        "credentials"
    )


def save_profile_config(profile_config=None):
    profile_config_path = get_profile_config_path()

    with open(profile_config_path, 'w') as file:
        profile_config.write(file)


def get_profile_config():
    profile_config_path = get_profile_config_path()

    profile_config = ConfigParser()

    if os.path.isfile(profile_config_path):
        profile_config.read(
            filenames=profile_config_path,
            encoding="UTF-8"
        )

    return profile_config
