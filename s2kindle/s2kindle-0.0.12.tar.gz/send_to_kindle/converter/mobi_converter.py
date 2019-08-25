from pathlib import Path
from subprocess import run  # nosec


def html_to_mobi(kindlegen_path, input_path, file_name):
    new_env = {"PATH": str(kindlegen_path.resolve())}

    result = run(
        ["kindlegen", "-o", f"{file_name}.mobi", str(input_path.resolve())],
        env=new_env,  # nosec
    )
    if not result.returncode == 0 and not result.returncode == 1:
        raise ValueError()

    return Path(input_path.parent, f"{file_name}.mobi")
