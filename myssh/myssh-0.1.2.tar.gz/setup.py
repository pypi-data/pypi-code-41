
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop


class InstallWrapper(install):

    def run(self):
        install.run(self)
        from alembic.config import Config
        from alembic import command
        import os
        import ssh_app
        # try:
        #     os.mkdir('/etc/myssh')
        # except OSError:
        #     pass
    
        main_link = os.path.dirname(os.path.abspath(ssh_app.__file__))
        print(main_link)
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "ssh_app:migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///{}/ssh.db".format(main_link))
        # alembic_cfg.set_main_option(
        #     "sqlalchemy.url", "sqlite:///{}/ssh.db".format(main_link))
        command.upgrade(alembic_cfg, "head")



class InstallWrapperD(develop):

    def run(self):
        develop.run(self)
        from alembic.config import Config
        from alembic import command
        import os
        import ssh_app
        # try:
        #     os.mkdir('/etc/myssh')
        # except OSError:
        #     pass
        main_link = os.path.dirname(os.path.abspath(ssh_app.__file__))

        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "ssh_app:migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///{}/ssh.db".format(main_link))
        # alembic_cfg.set_main_option(
        #     "sqlalchemy.url", "sqlite:///{}/ssh.db".format(main_link))
        command.upgrade(alembic_cfg, "head")


setup(
    name='myssh',
    version='0.1.2',
    author='Ahmed Khatab',
    author_email='ahmmkhh@gmail.com',
    packages=['ssh_app', 'ssh_app.migrations', 'ssh_app.migrations.versions'],
    scripts=['bin/con', 'bin/sshentry'],
    url='http://pypi.python.org/pypi/myssh/',
    license='LICENSE.txt',
    description='Useful ssh acess tool.',
    long_description=open('README.txt').read(),
    install_requires=['alembic==1.0.11', 'SQLAlchemy==1.3.6',
                      'argcomplete==1.10.0'

                      ],
    cmdclass={'install': InstallWrapper,
              'develop': InstallWrapperD},
    include_package_data=True
)
