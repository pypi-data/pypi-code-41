import datetime

from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class ResourceModel(BaseModel):
    __tablename__ = 'resources'

    id = Column('id', Integer, primary_key=True)
    resource_id = Column('resource_id', String(255), default='', nullable=False)
    job_id = Column('job_id', String(255), default='', nullable=False)
    status = Column('status', String(255), default='', nullable=False)
    created_at = Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column('updated_at', TIMESTAMP, onupdate=datetime.datetime.utcnow)
