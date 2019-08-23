import os
import platform
import tempfile
from conans.util.config_parser import ConfigParser

import requests

from conan_index_tools.index_storage import IndexStorage, USER_CHANNEL
from conan_index_tools.tools import environment_append


def get_docker_image_name(settings):
    docker_image = "conanio/{}{}".format(settings["compiler"],
                                         settings["compiler.version"].replace(".", ""))
    return docker_image


def _get_settings(profile_path):
    with open(profile_path) as fp:
        contents = fp.read()
    doc = ConfigParser(contents, allowed_fields=["build_requires", "settings", "env",
                                                 "scopes", "options"])
    settings = {}
    for line in doc.settings.splitlines():
        chunks = line.split("=")
        settings[chunks[0]] = chunks[1]
    return settings


def get_profile_path(profile_name):
    home = os.environ.get("CONAN_USER_HOME", os.path.expanduser("~/.conan"))
    return os.path.abspath(os.path.expanduser(os.path.join(home, "profiles", profile_name)))


def run_create(index_path, ref, profile_name, profile_url):

    if profile_name and profile_url:
        raise Exception("Do not specify profile and profile_url")

    if profile_url:
        try:
            r = requests.get(profile_url, allow_redirects=True)
            profile_text = r.content
            tmp_path = tempfile.mkdtemp()
            profile_path = os.path.join(tmp_path, "profile.txt")
            with open(profile_path, "w") as fd:
                try:
                    profile_text = profile_text.decode()
                except:
                    pass
                fd.write(profile_text)
        except Exception as e:
            print("Error downloading the file: {}".format(e))
            exit(-1)
    elif profile_name:
        profile_path = get_profile_path(profile_name)
    else:
        profile_path = get_profile_path("default")

    cur_os = {"Darwin": "Macos"}.get(platform.system(), platform.system())
    storage = IndexStorage(index_path)
    settings = _get_settings(profile_path)

    if settings["os_build"] != "Linux" and cur_os != settings["os_build"]:
        raise Exception("Cannot run a build of {} in this system".format(settings["os_build"]))

    recipe_folder = storage.real_recipe_folder(*ref.split("/"))
    print("Running at: {}".format(recipe_folder))

    my_env = os.environ.copy()

    if ((settings and settings["os_build"] == "Linux") or
       (not settings and cur_os == "Linux")) and docker_present():
        docker_image = get_docker_image_name(settings)
        create = "conan profile list && conan create recipe {}@{}".format(ref, USER_CHANNEL)
        inside = "pip uninstall -y conan-package-tools && " \
                 "pip install conan --upgrade &&" \
                 "rm -rf ./recipe/test_package/build && " + create
        cmd = 'docker run --rm -v{}:/home/conan/recipe -v{}:/home/conan/profiles ' \
              '-e CONAN_HOOK_ERROR_LEVEL=40 -e CONAN_USER_HOME=/home/conan/ ' \
              '{} /bin/bash -c "{}"'.format(recipe_folder, os.path.dirname(profile_path),
                                            docker_image, inside)
    else:
        cmd = "conan create . {}@{} --profile {}".format(ref, profile_path, USER_CHANNEL)
        my_env["CONAN_HOOK_ERROR_LEVEL"] = "40"

    print("---------------------  RUNNING  ---------------------\n{}\n".format(cmd))
    with environment_append(my_env):
        tmp = os.getcwd()
        os.chdir(recipe_folder)
        code = os.system(cmd)
        os.chdir(tmp)
        if code != 0:
            raise Exception("The command '{}' failed! ".format(cmd))


def docker_present():
    return os.system("which docker") == 0
