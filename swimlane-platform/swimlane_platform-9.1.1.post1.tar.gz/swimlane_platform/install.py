import subprocess
import sys
from os import path
import os
import stat
import pkg_resources
import swimlane_platform
from swimlane_platform.lib import ValidationException, \
    ArgsConfigQuestions, \
    info_function_start_finish, \
    debug_function_args, \
    Configuration, \
    BaseWithLog, \
    names, \
    DockerComposeManager, \
    PathExistsValidator, \
    VersionValidator, \
    AnswerRequiredValidator, \
    DockerManager, \
    DockerComposeFileManager
from swimlane_platform.enable_ssl import run as run_enable_ssl
from swimlane_platform.add_file_encryption_key import run as run_add_file_encryption
import shutil
import glob
from json import load


def find_remote_sibling(location, name):
    folder = path.join(location, name)
    if path.exists(folder):
        return folder
    elif location == '/':
        return None
    else:
        return find_remote_sibling(path.dirname(location), name)


class SwimlaneInstaller(BaseWithLog):

    def __init__(self, args):
        # type: (Configuration) -> None
        super(SwimlaneInstaller, self).__init__(args)
        self.script_path = path.dirname(path.realpath(__file__))
        self.template_dir = find_remote_sibling(self.script_path, names.TEMPLATE_DIR)

    @info_function_start_finish('Install Swimlane.')
    def run(self):
        """
        Main Swimlane install method.
        """
        self.partial_pre_flight_check()
        self.install_swimlane_files()
        self.get_swimlane_images()
        self.run_old_script()
        run_enable_ssl(self.args.to_dict())
        run_add_file_encryption(self.args.to_dict())
        self.run_after_install()

    @info_function_start_finish('Partial pre-flight checks.')
    def partial_pre_flight_check(self):
        self.check_docker_repository_access()

    @info_function_start_finish('Installing Swimlane files.')
    def install_swimlane_files(self):
        """
        Make install directories and copy files there
        """
        self.create_if_does_not_exists(names.INSTALL_DIR)
        secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        self.create_if_does_not_exists(secrets_dir)
        db_init_dir = path.join(names.INSTALL_DIR, names.DB_INIT_SUB_FOLDER)
        self.create_if_does_not_exists(db_init_dir)
        self.copy_if_does_not_exists(self.template_dir, names.INSTALL_DIR, '*.yml')
        self.copy_if_does_not_exists(path.join(self.template_dir, names.DB_INIT_SUB_FOLDER), db_init_dir, '*.sh')
        self.copy_if_does_not_exists(path.join(self.template_dir, names.SECRETS_SUB_FOLDER), secrets_dir, '.*')

    @info_function_start_finish('Getting Swimlane docker images.')
    def get_swimlane_images(self):
        """Loads or pulls docker images required by Swimlane.
        In case of offline, analyses the images bundled, until build will know or care about repository
        re-tags nexus images. In case of online, analyses docker-compose file template and decides
        which version to pull.
        In both cases modifies docker-compose template to use correct images.
        """
        docker_manager = DockerManager(self.logger)
        docker_compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        docker_compose_file_manager = DockerComposeFileManager(self.logger, docker_compose_file)
        repository = names.DEV_REPOSITORY if self.args.dev else ''
        version = str(self.args.version) if self.args.version else self.latest_version()
        if self.args.installer_is_offline:
            images_file = path.join(self.args.extracted_files_folder, names.DOCKER_IMAGE_ARCHIVE_NAME)
            images = docker_manager.image_load(images_file)
            if not self.args.dev:
                for tag in (str(image.tags[0]) for image in images):
                    if tag.startswith(names.DEV_REPOSITORY):
                        new_tag = tag.replace(names.DEV_REPOSITORY, repository)
                        docker_manager.image_re_tag(tag, new_tag)
                        version = new_tag.split(':')[-1]
            for tag in (str(image.tags[0]) for image in images):
                self.logger.verbose("{image} loaded from archive.".format(image=tag))
        else:
            template_image_tags = docker_compose_file_manager.get_image_tags()
            for template_image_tag in template_image_tags:
                image_tag = template_image_tag \
                    .replace(names.TEMPLATE_REPOSITORY_TAG, repository) \
                    .replace(names.TEMPLATE_VERSION_TAG, version)
                docker_manager.image_pull(image_tag)
                self.logger.verbose("{image} docker image pulled.".format(image=image_tag))

        docker_compose_file_manager.replace_in_file_and_reload(names.TEMPLATE_REPOSITORY_TAG, repository)
        docker_compose_file_manager.replace_in_file_and_reload(names.TEMPLATE_VERSION_TAG, version)

    @staticmethod
    def latest_version():
        # type: () -> str
        """ Returns the latest version of swimlane platform.
        :return: swimlane platform package version.
        """
        return '9.1.1'
        # return pkg_resources.get_distribution(swimlane_platform.__name__).version

    @info_function_start_finish('Running old swimlane script.')
    def run_old_script(self):
        """
        Runs old installation script.
        """
        install_script = path.join(find_remote_sibling(self.script_path, 'swimlane_scripts'), 'install.sh')
        if not install_script:
            raise ValidationException('Script file not found.')
        st = os.stat(install_script)
        os.chmod(install_script, st.st_mode | stat.S_IEXEC)
        commands = [install_script, '--install-template-folder', self.template_dir]
        system_args = sys.argv[1:] if len(sys.argv) > 1 else []
        commands.extend(system_args)
        if self.args.log and '--log' not in system_args:
            commands.extend(['--log', self.args.log])
        if self.args.dev and '--dev' not in system_args:
            commands.append('--dev')
        subprocess.check_output(commands)

    @info_function_start_finish('After installation.')
    def run_after_install(self):
        # type: () -> None
        """
        Prompts the user and starts or leaves containers as is.
        """
        questions = [{
            'type': 'confirm',
            'name': 'start_swimlane',
            'message': 'Would you like to start the Swimlane services?'
        }]
        config_manager = ArgsConfigQuestions(self.args.to_dict())
        config_manager.collect(questions)
        args = config_manager.to_arguments()
        if args.start_swimlane:
            docker_compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
            DockerComposeManager(self.logger, docker_compose_file).docker_compose_up()
        else:
            self.logger.info(
                'To start the Swimlane Services manually, cd /opt/swimlane and run "docker-compose up -d".')

    @debug_function_args
    def create_if_does_not_exists(self, dir_path):
        """Creates directory first checking for it's existence."""
        if not path.exists(dir_path):
            os.mkdir(dir_path)
            self.logger.verbose("{source} directory created.".format(source=dir_path))

    @debug_function_args
    def copy_if_does_not_exists(self, source, target, mask):
        for filepath in glob.glob1(source, mask):
            if not path.exists(path.join(target, filepath)):
                source_file = path.join(source, filepath)
                shutil.copy2(source_file, target)
                self.logger.verbose("File {source} copied to {target}".format(source=source_file, target=target))

    def check_docker_repository_access(self):
        if self.args.installer_is_offline:
            return
        with open(path.expanduser('~/.docker/config.json')) as fs:
            docker_config = load(fs)
        registered_repositories = [str(key) for key, value in docker_config['auths'].items()]
        repo_name = names.DEV_REPOSITORY.rstrip('/') if self.args.dev else 'https://index.docker.io/v1/'
        if not [1 for repository in registered_repositories if repo_name in repository]:
            questions = [
                {
                    'type': 'confirm',
                    'name': 'collect_docker_login',
                    'message': 'You are not logged in to {name}, log in now?'.format(name=repo_name)
                },
                {
                    'type': 'input',
                    'name': 'docker_repo_user',
                    'message': '{name} user name?'.format(name=repo_name),
                    'when': lambda a: 'collect_docker_login' in a and a['collect_docker_login'],
                    'validate': AnswerRequiredValidator
                },
                {
                    'type': 'input',
                    'name': 'docker_repo_password',
                    'message': '{name} password?'.format(name=repo_name),
                    'when': lambda a: 'collect_docker_login' in a and a['collect_docker_login'],
                    'validate': AnswerRequiredValidator
                }]
            config_manager = ArgsConfigQuestions(self.args.to_dict())
            config_manager.collect(questions)
            self.args = config_manager.to_arguments()
            if not self.args.docker_repo_user or not self.args.docker_repo_password:
                raise ValidationException("Cannot proceed without login to {name}.".format(name=repo_name))
            docker_manager = DockerManager(self.logger)
            docker_manager.login(repo_name, self.args.docker_repo_user, self.args.docker_repo_password)


def run(parent_config):
    # type: (ArgsConfigQuestions) -> None
    # noinspection PyCompatibility
    questions = [
        {
            'type': 'confirm',
            'name': 'installer_is_offline',
            'message': 'Are you installing offline?'
        },
        {
            'type': 'input',
            'name': 'extracted_files_folder',
            'message': 'Where are the extracted files located?',
            'when': lambda a: 'installer_is_offline' in a and a['installer_is_offline'],
            'default': u'.',
            'validate': PathExistsValidator
        },
        {
            'type': 'input',
            'name': 'version',
            'message': 'For development installation which version do you want to use?',
            'default': unicode(SwimlaneInstaller.latest_version()),
            'validate': VersionValidator,
            'when': lambda a: ('dev' in a and a['dev'])
                              and not ('installer_is_offline' in a and a['installer_is_offline'])
        }
    ]
    config = ArgsConfigQuestions(parent_config)
    config.collect(questions)
    installer = SwimlaneInstaller(config.to_arguments())
    installer.run()
