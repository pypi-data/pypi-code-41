from aioli import Package

from .service import DatabaseService
from .config import ConfigSchema


export = Package(
    controllers=[],
    services=[DatabaseService],
    config=ConfigSchema,
    auto_meta=True
)
