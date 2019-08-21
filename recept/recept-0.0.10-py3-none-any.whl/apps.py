import sys

import sh


def app(name, *args, _out=sys.stdout, _err=sys.stderr, _tee=True, **kwargs):
    try:
        return sh.Command(name).bake(
            *args, _out=_out, _err=_err, _tee=_tee, **kwargs
        )
    except sh.CommandNotFound:
        return sh.Command(sys.executable).bake(
            "-c",
            (
                f"import sys; import click; click.secho('Command `{name}` "
                f"not found', fg='red'); sys.exit(1)"
            ),
        )


# Shell commands
ls = app("ls")
rm = app("rm", "-rf")
cp = app("cp", "-rf")
find = app("find", _out=None)
mount = app("mount")
umount = app("umount", "-f")


# Python commands
python = app(sys.executable)
pip = app("pip")
pytest = app("py.test", "-s", _tee=False, _ok_code=[0, 1, 2, 3, 4, 5])
black = app("black")
flake8 = app("flake8", _ok_code=[0, 1])
pydocstyle = app("pydocstyle", _ok_code=[0, 1])


# Docker
docker = app("docker")
