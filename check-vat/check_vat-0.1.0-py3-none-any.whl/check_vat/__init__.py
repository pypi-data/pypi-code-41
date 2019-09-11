"""Check VAT main"""
__all__ = ['is_valid_vat']

from zeep import Client

VIES_URL = "http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"


def is_valid_vat(vat_id: str):
    vat = vat_id.replace(" ","").strip()
    client = Client(VIES_URL)
    result = client.service.checkVat(countryCode=vat[:2], vatNumber=vat[2:])
    # {
    #     'countryCode': 'DE',
    #     'vatNumber': '308316836',
    #     'requestDate': datetime.date(2019, 9, 11),
    #     'valid': True,
    #     'name': '---',
    #     'address': '---'
    # }
    return result['valid']
