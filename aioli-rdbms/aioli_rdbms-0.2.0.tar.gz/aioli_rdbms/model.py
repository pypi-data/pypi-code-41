from orm import models, fields


class ModelMeta(models.ModelMetaclass):
    def __new__(cls, name, bases, attrs):
        new_cls = super(models.ModelMetaclass, cls).__new__(
            cls, name, bases, attrs
        )

        mod_name = new_cls.__module__.split(".")[0]
        new_cls.__tablename__ = f"{mod_name}__{new_cls.__tablename__}"
        new_cls.__related__ = {}

        new_cls.columns = {}
        pkname = None

        for name, field in new_cls.fields.items():
            if field.primary_key:
                pkname = name

            new_cls.columns[name] = field.get_column(name)

        new_cls.__pkname__ = pkname

        return new_cls


class Model(models.Model, metaclass=ModelMeta):
    __metadata__ = None
    __tablename__ = None
    __table__ = None
    __registered__ = False
