from sqlalchemy import MetaData, Table

from aioli.service import BaseService

from .model import fields
from .proxy import ModelProxy
from .manager import DatabaseManager


class DatabaseService(BaseService):
    loggers = ["sqlalchemy", "databases"]
    _models_registered = []

    async def on_startup(self):
        mgr = DatabaseManager

        if not mgr.configured:
            await mgr.install(self.config)

        for model in self._models_registered:
            model.__database__ = mgr.database

        if self.pkg.memory["db_metadata"]:
            self.pkg.memory["db_metadata"].create_all(mgr.engine)

    async def on_shutdown(self):
        self.log.debug("Disconnecting from database")
        await DatabaseManager.disconnect()

    def use_model(self, model):
        """Factory method for creating a ModelProxy

        :param model: Model class
        :return: ModelProxy instance
        """

        if model.__registered__ is False:
            model = self._register_model(model)

        return ModelProxy(model)

    def _register_model(self, model):
        """Associates a model with package

        Uses metadata for this Service's Package to register the given model.

        :param model: aioli_rdbms.Model class
        """

        assert model.__registered__ is False, f"Model {model} has already been registered"

        state = self.pkg.memory

        if not state["db_metadata"]:
            state["db_metadata"] = MetaData()

        self.log.info(f"Registering Model: {model.__name__} [{model.__tablename__}]")

        for name, field in model.fields.items():
            if isinstance(field, fields.ForeignKey):
                related_mdl = field.to
                if related_mdl.__registered__ is False:
                    self._register_model(related_mdl)

                model.__related__[name] = related_mdl

        model.__metadata__ = state["db_metadata"]
        model.__table__ = Table(model.__tablename__, state["db_metadata"], *model.columns.values())
        model.__registered__ = True

        self._models_registered.append(model)

        return model
