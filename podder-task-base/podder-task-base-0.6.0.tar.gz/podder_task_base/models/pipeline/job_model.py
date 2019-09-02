import datetime

from sqlalchemy import JSON, TIMESTAMP, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class JobModel(BaseModel):
    __tablename__ = 'jobs'

    id = Column('id', Integer, primary_key=True)
    job_id = Column('job_id', String(255), default='', nullable=False)
    dag_id = Column('dag_id', String(255), default='', nullable=False)
    status = Column('status', String(255), default='', nullable=False)
    job_data = Column('job_data', JSON, default='')
    created_at = Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column('updated_at', TIMESTAMP, onupdate=datetime.datetime.utcnow)
