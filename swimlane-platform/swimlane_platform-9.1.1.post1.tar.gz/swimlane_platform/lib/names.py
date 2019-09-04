# noinspection PyPep8Naming
class names:
    DOCKER_IMAGE_ARCHIVE_NAME = 'swimlane-images.tgz'
    TEMPLATE_REPOSITORY_TAG = '<sw_docker_image_repo_placeholder>'
    TEMPLATE_VERSION_TAG = '<sw_docker_image_tag_placeholder>'
    DEV_REPOSITORY = 'nexus.swimlane.io:5000/'
    DB_INIT_SCRIPT = 'init-mongodb-users.sh'
    SWIMLANE_PREFIX = 'SWIMLANE_'
    APP_NAME = 'swimlane_platform'
    AUTOMATION = 'automation'
    AUTOMATION_FILE = 'automation_file'
    DOCKER_COMPOSE_OVERRIDE_FILE = 'docker-compose.override.yml'
    DOCKER_COMPOSE_INSTALL_FILE = 'docker-compose.install.yml'
    SECRETS_SUB_FOLDER = '.secrets/'
    DB_INIT_SUB_FOLDER = 'db-init'
    TEMPLATE_DIR = 'swimlane_template_dir'
    SW_API = 'sw_api'
    SW_WEB = 'sw_web'
    SW_NEO_J = 'sw_neo4j'
    SW_TASKS = 'sw_tasks'
    SW_MONGO = 'sw_mongo'
    DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    API_ENV_FILE = '.api-env'
    TASKS_ENV_FILE = '.tasks-env'
    DOT_NET_SWIMLANE_CONN_KEY = 'SWIMLANE_Data__Mongo__SwimlaneConnectionString'
    DOT_NET_ADMIN_CONN_KEY = 'SWIMLANE_Data__Mongo__AdminConnectionString'
    INSTALL_DIR = '/opt/swimlane'

    def __init__(self):
        pass

