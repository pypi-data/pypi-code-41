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


class SxclzySchedule(Base):
    __tablename__ = 'sxclzy_schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    func_name = Column(String(255), nullable=False)
    func = Column(LargeBinary, nullable=False)
    schedule = Column(LargeBinary, nullable=False)
    run_times = Column(Integer, nullable=False)
    args = Column(LargeBinary, nullable=True)
    status = Column(Integer, nullable=False, default=0)
    create_time = Column(String(25))

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


model_dic = {
    'SxclzySchedule': SxclzySchedule,
}


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
