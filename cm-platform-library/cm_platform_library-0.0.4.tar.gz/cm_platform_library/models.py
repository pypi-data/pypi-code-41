from cm_service_library.helpers import generate_uuid_str
from sqlalchemy import Column, Index, Text, Boolean, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class License(Base):
    __tablename__ = 'licenses'

    license_id = Column(Text, primary_key=True, default=generate_uuid_str)
    is_master = Column(Boolean, default=False)
    meta_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_licenses_meta_data', meta_data, postgresql_using="gin"),
    )


class Provider(Base):
    __tablename__ = 'providers'

    provider_id = Column(Text, primary_key=True, default=generate_uuid_str)
    parent_provider_id = Column(Text, index=True, nullable=True)
    provider_external_id = Column(Text, index=True, nullable=True)
    license_id = Column(Text, index=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    provider_secret = Column(Text, index=True, nullable=False)

    name = Column(Text, nullable=False)
    meta_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_providers_meta_data', meta_data, postgresql_using="gin"),
        Index('idx_providers_name_license', name, license_id, unique=True),
    )


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Text, primary_key=True, default=generate_uuid_str)
    license_id = Column(Text, index=True, nullable=False)
    provider_id = Column(Text, index=True, nullable=True)
    trusted = Column(Text, index=True, nullable=False, default=False,
                     comment="Used to indicate whether the license &/or provider trusts this user. For example "
                             "a user that signs up via the internet for a service is NOT a trusted user.")

    meta_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_users_meta_data', meta_data, postgresql_using="gin"),
    )


class ProviderRequest(Base):
    __tablename__ = 'provider_requests'

    request_ref = Column(BigInteger, autoincrement=True, primary_key=True)
    request_id = Column(Text, unique=True, default=generate_uuid_str)

    license_id = Column(Text, index=True, nullable=False)
    provider_id = Column(Text, index=True, nullable=False)
    user_id = Column(Text, nullable=True)
    endpoint = Column(Text, index=True, nullable=False)

    meta_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
