import distutils.spawn
import os
import subprocess

from powerline.theme import requires_segment_info

g_env_pyenv_keys = ["PYENV_VERSION", "PYENV_DIR"]
g_env_virtualenv_key = "VIRTUAL_ENV"


# Remove ENV vars injected to powershell by pyenv
for key in g_env_pyenv_keys:
    os.unsetenv(key)


@requires_segment_info
def pyenv(pl, segment_info):
    global g_env_pyenv_keys, g_env_virtualenv_key
    env = segment_info["environ"]
    # Check for shell spawned by virtualenv(used by pipenv) first
    if distutils.spawn.find_executable("pipenv") and g_env_virtualenv_key in env:
        py_version = os.path.basename(env[g_env_virtualenv_key])
    else:
        for key in g_env_pyenv_keys:
            if key in env:
                os.putenv(key, env[key])
        cwd = segment_info["getcwd"]()
        py_version = subprocess.check_output(
            ["pyenv", "version-name"], cwd=cwd, encoding="utf8"
        ).strip()
    return [
        {
            "name": "pyenv_version",
            "type": "string",
            "contents": " {}".format(py_version),
            "highlight_groups": ["pyenv:version"],
        }
    ]
