from sdkBraspag.Enums import DocumentType, BankAccountType, AttachementType
from .PaymentArrangement import PaymentArrangement
from .ExceptionOnboarding import ExceptionOnboarding
import requests
import json


class Onboarding:
    def __init__(self, token, sandbox=True):
        self.__token = token

        if sandbox is True:
            self.__base_url = 'https://splitonboardingsandbox.braspag.com.br'
        else:
            self.__base_url = 'https://splitonboarding.braspag.com.br'

        self.__merchant_data = None
        self.__bank_account = None
        self.__address = None
        self.__notification = None
        self.__attachments = None
        self.__agreement = None

    def merchant_data(self, corporatename: str, fancyname: str, document_number: str, document_type: DocumentType,
                      contact_name: str, contact_phone: str, mail_address: str, merchant_category_code: int = '0000',
                      website: str = ''):
        merchant_data = dict(corporatename=corporatename,
                             fancyname=fancyname,
                             documentnumber=document_number,
                             documenttype=document_type,
                             merchantcategorycode=merchant_category_code,
                             contactname=contact_name,
                             contactphone=contact_phone,
                             mailaddress=mail_address,
                             website=website)
        self.__merchant_data = merchant_data

    def bank_account(self, bank: str, bank_account_type: BankAccountType, number: str, verifier_digit: str,
                     agency_number: str, agency_digit: str, document_number: str, document_type: DocumentType,
                     operation: str = None):
        bank_account = dict(bank=bank,
                            bankaccounttype=bank_account_type,
                            number=number,
                            verifierdigit=verifier_digit,
                            agencynumber=agency_number,
                            agencydigit=agency_digit,
                            documentnumber=document_number,
                            documenttype=document_type,
                            operation=operation)
        self.__bank_account = bank_account

    def address(self, street: str, number: str, neighborhood: str, city: str, state: str, zipcode: str,
                complement: str = ''):
        address = dict(street=street,
                       number=number,
                       neighborhood=neighborhood,
                       city=city,
                       state=state,
                       zipcode=zipcode,
                       complement=complement)
        self.__address = address

    def notification(self, url, **kwargs):
        notification = dict(url=url,
                            headers=[{'key': k, 'value': kwargs.get(k)} for k in kwargs.keys()])

        self.__notification = notification

    def attachements(self, *args):
        attachments = [arg for arg in args]
        self.__attachments = attachments

    def attachement(self, attachmenttype: AttachementType, file_name: str, file_type: str, data: str):
        attachement = dict(attachmenttype=attachmenttype,
                           file=dict(name=file_name,
                                     filetype=file_type,
                                     data=data)
                           )
        return attachement

    def global_agreements(self, fee: int, mdr_percentage: float):
        agreement = dict(fee=fee,
                         mdrpercentage=mdr_percentage)
        self.__agreement = agreement

    def agreements(self, fee, *args: PaymentArrangement):
        agreement = dict(fee=fee,
                         MerchantDiscountRates=[mdr.make_arrangement() for mdr in args])
        self.__agreement = agreement

    def make_request(self):
        request = {}
        request.setdefault('CorporateName', self.__merchant_data.get('corporatename'))
        request.setdefault('FancyName', self.__merchant_data.get('fancyname'))
        request.setdefault('DocumentNumber', self.__merchant_data.get('documentnumber'))
        request.setdefault('DocumentType', self.__merchant_data.get('documenttype'))
        request.setdefault('MerchantCategoryCode', self.__merchant_data.get('merchantcategorycode'))
        request.setdefault('ContactName', self.__merchant_data.get('contactname'))
        request.setdefault('ContactPhone', self.__merchant_data.get('contactphone'))
        request.setdefault('MailAddress', self.__merchant_data.get('mailaddress'))
        request.setdefault('Website', self.__merchant_data.get('website'))

        request.setdefault('BankAccount', self.__bank_account)
        request.setdefault('Address', self.__address)
        request.setdefault('Notification', self.__notification)
        request.setdefault('Attachments', self.__attachments)
        request.setdefault('Agreement', self.__agreement)

        return request

    def send(self, request):
        endpoint = '/api/subordinates'
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {}'.format(self.__token)}

        response = requests.post(url=self.__base_url + endpoint, headers=headers, data=json.dumps(request))

        try:
            return response.json()
        except ExceptionOnboarding:
            raise ExceptionOnboarding(response.json())
        except Exception as error:
            raise Exception(error)
