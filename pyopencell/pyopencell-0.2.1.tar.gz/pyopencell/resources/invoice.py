from pyopencell.resources.base_resource import BaseResource


class Invoice(BaseResource):
    _name = "invoice"
    _url_path = ""

    invoiceId = 0
    invoiceType = ""
    billingAccountCode = ""
    sellerCode = ""
    subscriptionCode = ""
    orderNumber = ""
    dueDate = 0
    invoiceDate = 0
    categoryInvoiceAgregate = [{}]
    taxAggregate = [{}]
    invoiceNumber = ""
    amountWithoutTax = 0
    amountTax = 0
    amountWithTax = 0
    paymentMethod = "DIRECTDEBIT"
    pdfFilename = ""
    pdf = ""
    netToPay = 0
    invoiceMode = "DETAILLED"
    dueBalance = 0
    isDraft = True
