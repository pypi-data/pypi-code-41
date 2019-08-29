from sqlalchemy import Column, DateTime, String, Integer, func  
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SSHEntry(Base):  
    __tablename__ = 'ssh_entry'
    id = Column(Integer, primary_key=True)
    name =  Column(String,unique=True)
    host = Column(String, unique=True)
    user = Column(String)
    key_path = Column(String)
    when = Column(DateTime, default=func.now())

    def __repr__(self):
        return 'id: {}'.format(self.id)
