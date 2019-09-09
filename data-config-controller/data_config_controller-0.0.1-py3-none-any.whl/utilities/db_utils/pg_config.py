""" Postgres Configuration """
import utils


class PGConfig:
    """ All methods for postgres configuration """
    def __init__(self):
        """ Set up class variables """
        self.def_pg_config_path = utils.get_project_file('/json_libraries/postgres.json')
        self.env = utils.get_current_env()

    def get_db_dict(self, user, db_name):
        """
        Method to build the proper database dictionary to generate a connection
        :param user: User that will be running the SQL command
        :param db_name: Name of the database the command will be run against
        :return: Dictionary of the user and connection informaiton
        """
        db_dict = {}
        pg_dict = self.__read_default_pg_config_file()
        db_dict['host'] = pg_dict['db_connections'][db_name]['server']
        db_dict['port'] = pg_dict['db_connections'][db_name]['port']
        db_dict['dbname'] = pg_dict['db_connections'][db_name]['db_name']
        db_dict['username'] = pg_dict['user_credentials'][self.env][user]['user']
        db_dict['password'] = pg_dict['user_credentials'][self.env][user]['password']
        return db_dict

    def __read_default_pg_config_file(self):
        """
        Method to read the default config file for the postgres database
        :return: Dictionary of the default postgres.json config file
        """
        pg_dict = utils.get_json(self.def_pg_config_path)
        return pg_dict