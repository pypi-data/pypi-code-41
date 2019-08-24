from Enums import Product


class PaymentArrangement:
    def __init__(self, brand, product: Product, percent: float, initial_installment_number: int = 1,
                 final_installment_number: int = 1):

        self.__brand = brand
        self.__product = product
        self.__percent = percent

        if self.__product == Product.DebitCard:
            self.__initial_installment_number = 1
            self.__final_installment_number = 1
        else:
            self.__initial_installment_number = initial_installment_number
            self.__final_installment_number = final_installment_number

    def make_arrangement(self):
        paymentarrangement = dict(PaymentArrangement=dict(product=self.__product,
                                                          brand=self.__brand),
                                  InitialInstallmentNumber=self.__initial_installment_number,
                                  FinalInstallmentNumber=self.__final_installment_number,
                                  Percent=self.__percent)
        return paymentarrangement
