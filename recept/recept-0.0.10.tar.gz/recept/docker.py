from typing import List, Dict, Optional, Union

import click

from recept.apps import docker


def login(username: str, password: str, registry: str):
    """Login to docker registry.

    Args:
        username: Username.
        password: Password.
        registry: Url to the docker registry.
    """
    return docker.login(
        "--username", username, "--password", password, registry
    )


def remove_dangling_images():
    r = docker.images("-f", "dangling=true", "-q", _out=None)
    images = r.stdout.decode("utf-8").split()
    if len(images) > 0:
        docker.rmi(*images)


def build(
    dockerfile: str,
    image: str,
    tag: str = "latest",
    latest: bool = True,
    build_dir: str = ".",
):
    """Build docker container.

    Args:
        dockerfile: Path to the Dockerfile.
        image: Image name.
        tag: Build tag.
        latest: Tag the image with the latest tag too. (If the tag is not
            already "latest").
        build_dir: Build directory.

    """

    docker.build(
        "--file",
        dockerfile,
        "--tag",
        f"{image}:{tag}",
        "--network",
        "host",
        build_dir,
    )
    if latest and tag != "latest":
        docker.tag(f"{image}:{tag}", f"{image}:latest")


def pull(image: str, tag: str = "latest", registry: Optional[str] = None):
    """Pull the app image from ECR registry.

    Args:
        image: Image name.
        tag: Image tag.
        registry: Url to the registry. Default: docker hub.
    """
    docker.pull(
        f"{image}:{tag}" if registry is None else f"{registry}/{image}:{tag}"
    )


def push(image: str, tag: str = "latest", registry: Optional[str] = None):
    """Push app docker containers to registry.

    Args:
        image: Image name.
        tag: Image tag.
        registry: Url to the registry. Default: docker hub.
    """
    if registry is not None:
        # Tag the images with registry
        docker.tag(f"{image}:{tag}", f"{registry}/{image}:{tag}")
        image = f"{registry}/{image}:{tag}"
    else:
        image = f"{image}:{tag}"

    # Push images to registry
    docker.push(image)


def is_running(name: str):
    """Check if a container is running.

    Args:
        name: Name of the running container.
    """
    r = docker.ps("--filter", f"name={name}", "--format", "{{.Names}}")
    return f"{name}" in {
        line.strip() for line in r.stdout.decode("utf-8").splitlines()
    }


def create_network(network: str):
    """Create docker network if it doesn't already exist.

    Args:
        network: Network name.
    """
    r = docker.network.ls(
        "--filter", f"name={network}", "--format", "{{.Name}}"
    )
    if r.stdout.decode("utf-8").strip() != network:
        # Network does not exist, it should be created
        docker.network.create(network)


def start(
    name: str,
    image: str = None,
    tag: str = "latest",
    env: Optional[Dict[str, str]] = None,
    ports: Optional[Dict[int, int]] = None,
    volumes: Optional[Dict[str, str]] = None,
    networks: Optional[List[str]] = None,
    command: Optional[Union[str, List[str]]] = None,
    entrypoint: Optional[str] = None,
    interactive: bool = False,
):
    """Start a container.

    Args:
        name: Name of the container when started.
        image: Image to run. If image is not provided then:
            {registry}/{prefix}/{project} image will be used.
        tag: Image tag: Default: latest.
        env: Dictionary of environment variables that should be available to
            the container.
        ports: Dictionary or host_port -> guest_port mappings that should be
            exposed.
        volumes: Dictionary of host_path -> guest_path mappings that should be
            attached as volumes.
        networks: List of network names that the container should have access.
        command: Override of the default entrypoint of the container.
        entrypoint: Override of the default entrypoint.
        interactive: Should the container be started in interactive mode. If
            False, the container (or command) will be started in detached mode.
    """
    if is_running(name):
        click.secho(f"{name} is already running.", fg="red")
        return

    if interactive:
        docker_app = docker.bake(_fg=True)
        run_command = ["--interactive", "--tty", "--rm", "--name", name]
    else:
        docker_app = docker
        run_command = ["--detach", "--tty", "--rm", "--name", name]

    if entrypoint is not None:
        run_command.extend(["--entrypoint", entrypoint])

    # Add env
    if env is not None:
        for key, value in env.items():
            run_command.extend(["--env", f"{key}={value}"])

    # Add ports
    if ports is not None:
        for key, value in ports.items():
            run_command.extend(["--publish", f"{key}:{value}"])

    # Add volumes
    if volumes is not None:
        for key, value in volumes.items():
            run_command.extend(["--volume", f"{key}:{value}"])

    # Add networks
    if networks is not None:
        for network in networks:
            create_network(network)
            run_command.extend(["--network", network])

    # Add image
    run_command.append(f"{image}:{tag}")

    if command is None:
        docker_app.run(*run_command)
    else:
        if isinstance(command, str):
            command = [command]
        docker_app.run(*run_command, *command)


def stop(name: str):
    """Stop a running container.

    Args:
        name: Name of the running container.
    """
    if not is_running(name):
        click.secho(f"{name} is not running.", fg="red")
        return
    docker.stop(name)


def attach(name: str, command="sh"):
    """Attach to a running container.

    Args:
        name: Name of the running container.
        command: Command to run.
    """
    docker.bake(_fg=True).exec("--interactive", "--tty", name, command)
