from datetime import date
from enum import IntEnum

from schema import Schema, And, Use, Optional

from dcard_sdk.base_classes import ResponseExt, HandlerExt


class OwnerType(IntEnum):
    INDIVIDUAL = 1
    ENTITY = 2


class DocumentType(IntEnum):
    STS = 1
    PTS = 2


class Category(IntEnum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 6


class CustomsCategory(IntEnum):
    M1 = 2
    N1 = 3


class FuelType(IntEnum):
    PETROL = 1
    DIESEL = 2


class BrakeType(IntEnum):
    HYDRAULIC = 1
    PNEUMATIC = 2
    COMBINED = 3
    MECHANICAL = 4


class Response(ResponseExt):
    pass


class Handler(HandlerExt):
    endpoint = '/card'
    schema = Schema({
        'owner_type': And(OwnerType, Use(int)),
        Optional('owner_firm'): str,
        'owner_name': str,
        'owner_surname': str,
        Optional('owner_patronymic'): str,
        'document_type': And(DocumentType, Use(int)),
        'document_series': str,
        'document_number': str,
        'document_issued_date': And(date, Use(lambda x: x.strftime('%d.%m.%Y'))),
        'document_issued_by': str,
        'ts_category': And(Category, Use(int)),
        Optional('rc'): And(CustomsCategory, Use(int)),
        Optional('ts_reg_number'): str,
        Optional('ts_vin'): str,
        Optional('ts_body'): str,
        Optional('ts_frame'): str,
        'ts_mark': str,
        'ts_model': str,
        'ts_year': int,
        'ts_mass_base': int,
        'ts_mass_max': int,
        Optional('ts_mileage'): int,
        Optional('ts_fuel_type'): And(FuelType, Use(int)),
        'ts_brakes_type': And(BrakeType, Use(int)),
        'tires_id': int,
        'ts_taxi': And(bool, Use(int)),
        'ts_training': And(bool, Use(int)),
        'ts_dangerous': And(bool, Use(int)),
    })

    def __call__(self, data):
        url = self.get_url()
        payload = self.schema.validate(data)
        response = self.post(url, payload)
        return Response(response).data
