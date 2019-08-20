from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
import os
import sys
_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(_project_path)

from base.common.orm import sql_base
from base.common.orm import init_orm

import inspect
import importlib
# load all models for auto-generate
model_modules = [m for m in os.listdir('{}/src/models'.format(_project_path)) if m != '__init__.py' and m[-3:] == '.py']
for mm in model_modules:
    model_module = importlib.import_module('src.models.{}'.format(mm[:-3]))
    for _name in dir(model_module):
        if not _name.startswith('__'):
            _class = getattr(model_module, _name)
            if inspect.isclass(_class):
                globals().update({_name: _class})

orm_builder = init_orm()
sql_base.metadata.reflect(bind=orm_builder.orm().engine())
target_metadata = sql_base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
