import os

from sqlalchemy import create_engine, TEXT, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import datetime

path = os.path.join(os.getcwd(), 'sqlite.db')
# path = ':memory:'
engine = create_engine('sqlite:///{}?check_same_thread=False'.format(path), echo=False)
Base = declarative_base()


class ImageTemplate(Base):
    __tablename__ = 'image_templates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hash_str = Column(String(100), unique=True)
    template_type = Column(String(100), nullable=False)
    data = Column(TEXT, nullable=False)
    threshold = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(String(30), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


class ReplaceImages(Base):
    __tablename__ = 'replace_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hash_str = Column(String(100), unique=True)
    repl_type = Column(String(100), nullable=False)
    data = Column(TEXT, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(String(30), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


model_dic = {
    'ImageTemplate': ImageTemplate,
    'ReplaceImages': ReplaceImages,
}


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
