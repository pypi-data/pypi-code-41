import dataclasses
import enum
import json
import os
import shutil
import stat
import subprocess
import tarfile
import tempfile
import typing as t

import wget

TEMPLATE_SUFFIX = ".template"


class CoreID(str, enum.Enum):
    ARDUINO_AVR = "arduino:avr"
    ARDUINO_MBED = "arduino:mbed"
    ARDUINO_MEGAAVR = "arduino:megaavr"
    ARDUINO_NRF52 = "arduino:nrf52"
    ARDUINO_SAM = "arduino:sam"
    ARDUINO_SAMD = "arduino:samd"
    ARDUINO_SAMD_BETA = "arduino:samd_beta"
    ARROW_SAMD = "Arrow:samd"
    ATMEL_AVR_XMINIS_AVR = "atmel-avr-xminis:avr"
    EMORO_AVR = "emoro:avr"
    INDUSRUINO_SAMD = "industruino:samd"
    INTEL_ARC32 = "Intel:arc32"
    INTEL_I586 = "Intel:i586"
    INTEL_I686 = "Intel:i686"
    LITTLEBITS_AVR = "littleBits:avr"
    MICROSOFT_WIN10 = "Microsoft:win10"


@dataclasses.dataclass
class ConnectedBoard:
    fqbn: str
    port: str


class ArduinoCLI:
    BINARY_URL = "https://github.com/arduino/arduino-cli/releases/download/0.4.0/arduino-cli_0.4.0_Linux_64bit.tar.gz"
    EXECUTABLE_NAME = "arduino-cli"

    def __init__(
        self,
        install_cores: t.Optional[t.List[str]] = None,
        bin_dir: t.Optional[str] = None,
    ):
        self._install_cores = install_cores
        self._persistent = bin_dir is not None
        self._temp_dir = None
        self._bin_dir = bin_dir or ""
        self.executable = os.path.join(self._bin_dir, self.EXECUTABLE_NAME)

    def download_binary_tar(self) -> str:
        return wget.download(self.BINARY_URL, self._bin_dir)

    def run_cmd(self, *args: str, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.run(args, **kwargs)

    def ensure_bin_dir_exists(self):
        if self._persistent:
            os.makedirs(self._bin_dir, exist_ok=True)
        else:
            self._temp_dir = tempfile.TemporaryDirectory()
            self._bin_dir = self._temp_dir.name
            self.executable = os.path.join(self._bin_dir, self.EXECUTABLE_NAME)

    def install_arduino_cli(self):
        if not os.path.isfile(self.executable):
            self.ensure_bin_dir_exists()
            tar_file = self.download_binary_tar()
            with tarfile.open(tar_file) as tar:
                tar.extractall(self._bin_dir)
        self.run("core", "update-index")
        if self._install_cores is None:
            self._install_cores = self.core_search()
        for core in self._install_cores:
            self.core_install(core)

    def __enter__(self):
        self.install_arduino_cli()
        return self

    def __exit__(self, type_, value, traceback):
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
        return False

    def run(self, *args, capture_output=False):
        if capture_output:
            args = list(args)
            args.extend(["--format", "json"])
        result = self.run_cmd(
            self.executable,
            *args,
            capture_output=capture_output,
            encoding="utf-8",
            env={"HOME": self._bin_dir},
        )
        result.check_returncode()
        if capture_output:
            return json.loads(result.stdout)

    def core_search(self, query: str = "") -> t.List[str]:
        outputs = self.run("core", "search", f"{query}", capture_output=True)
        return [output["ID"] for output in outputs]

    def core_install(self, core_id: str) -> None:
        self.run("core", "install", core_id)

    def compile_sketch(self, sketch: str, fqbn: str) -> None:
        self.run("compile", "--fqbn", fqbn, sketch)

    def upload_sketch(self, sketch: str, fqbn: str, port: str) -> None:
        self.run("upload", "-p", port, "--fqbn", fqbn, sketch)

    def connected_boards(self) -> t.List[ConnectedBoard]:
        output = self.run("board", "list", capture_output=True)
        ports = output.get("ports", [])
        boards = []
        for port in ports:
            boards_list = port.get("boards", [])
            if not boards_list:
                continue
            boards.append(
                ConnectedBoard(fqbn=boards_list[0]["FQBN"], port=port["address"])
            )
        return boards

    def compile_and_upload_to_connected(self, sketch_folder: str) -> None:
        for board in self.connected_boards():
            self.compile_sketch(sketch_folder, board.fqbn)
            self.upload_sketch(sketch_folder, board.fqbn, board.port)


def compile_and_upload_sketch(
    sketch_folder: str,
    install_cores: t.Optional[t.List[str]] = None,
    arduino_cli_dir: str = None,
):
    with ArduinoCLI(
        install_cores=install_cores, bin_dir=arduino_cli_dir
    ) as arduino_cli:
        arduino_cli.compile_and_upload_to_connected(sketch_folder)


def build_template(template_path: str, context: t.Any, output_path: str) -> None:
    with open(template_path) as template_file:
        content = template_file.read()
    content = content.format(context=context)
    with open(output_path, "w") as output_file:
        output_file.write(content)


def build_templates(template_dir: str, context: t.Any, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(template_dir):
        for dirname in dirnames:
            full_name = os.path.join(dirpath, dirname)
            relative_name = os.path.relpath(full_name, start=template_dir)
            os.mkdir(os.path.join(output_dir, relative_name))
        for filename in filenames:
            full_name = os.path.join(dirpath, filename)
            relative_name = os.path.relpath(full_name, start=template_dir)
            if full_name.endswith(TEMPLATE_SUFFIX):
                output_name = os.path.join(
                    output_dir, relative_name[: -len(TEMPLATE_SUFFIX)]
                )
                build_template(full_name, context, output_name)
            else:
                shutil.copy(full_name, os.path.join(output_dir, relative_name))


def compile_and_upload_template(
    template_dir: str,
    context: t.Any,
    install_cores: t.Optional[t.List[str]] = None,
    arduino_cli_dir: str = None,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_sketch_dir = os.path.join(
            temp_dir, os.path.basename(os.path.abspath(template_dir))
        )
        build_templates(template_dir, context, temp_sketch_dir)
        compile_and_upload_sketch(temp_sketch_dir, install_cores, arduino_cli_dir)
