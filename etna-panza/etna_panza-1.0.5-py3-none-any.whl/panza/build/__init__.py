import quixote
from quixote import new_context
from quixote.build import GeneratorType
from quixote.build.output import new_output, get_output
from textwrap import dedent


class AbstractScriptGenerator:
    """
    Base class for all setup script generators
    """

    def generate_script(self, blueprint: quixote.Blueprint, extra_context: dict = None) -> str:
        """
        Generate the setup script for a given blueprint

        :param blueprint:               the blueprint whose setup script to generate
        :param extra_context:           entries to add to the setup context
        """
        pass

    def generate_to_file(self, blueprint: quixote.Blueprint, path, extra_context: dict = None):
        """
        Generate the setup script for a given blueprint and save it into a file

        :param blueprint:               the blueprint whose setup script to generate
        :param path:                    the path of the file in which the script should be generated
        :param extra_context:           entries to add to the setup context
        """
        with open(path, "w") as f:
            f.write(self.generate_script(blueprint, extra_context))


class DockerScriptGenerator(AbstractScriptGenerator):
    """
    Script generator class for Dockerfiles
    """

    def generate_script(self, blueprint: quixote.Blueprint, extra_context: dict = None) -> str:
        extra_context = extra_context or {}
        with new_context(**extra_context, generator=GeneratorType.DOCKER), new_output():
            for command in blueprint.builders:
                command()
            commands = '\n'.join(get_output())
            return dedent(f"""
            FROM etnajawa/quixote-base
            VOLUME /moulinette

            {commands}
            """)


class ShellScriptGenerator(AbstractScriptGenerator):
    """
    Script generator class for shell scripts
    """

    def generate_script(self, blueprint: quixote.Blueprint, extra_context: dict = None) -> str:
        extra_context = extra_context or {}
        with new_context(**extra_context, generator=GeneratorType.SHELL), new_output():
            for command in blueprint.builders:
                command()
            return "#!/usr/bin/env bash\n" + '\n'.join(get_output()) + "\n"


def create_script_generator(generator_type: GeneratorType) -> AbstractScriptGenerator:
    """
    Create the appropriate script generator given its type

    :param generator_type:              the type of the generator to create
    """
    generators = {
        GeneratorType.DOCKER: DockerScriptGenerator,
        GeneratorType.SHELL: ShellScriptGenerator,
    }
    return generators[generator_type]()
