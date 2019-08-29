# Created by MysteryBlokHed in 2019.
class BasicOrder(object):
    def __init__(self, number, order_id, date, payment_status, fulfillment_status, total):
        self._dict = {}
        
        # Type checking
        if type(number) is int:
            self._dict["number"] = number
        else:
            raise TypeError(f"Expected int for number, got {type(number).__name__}.")
        if type(order_id) is str:
            self._dict["order_id"] = order_id
        else:
            raise TypeError(f"Expected str for order_id, got {type(order_id).__name__}.")
        if type(date) is str:
            self._dict["date"] = date
        else:
            raise TypeError(f"Expected str for date, got {type(date).__name__}.")
        if type(payment_status) is str:
            self._dict["payment_status"] = payment_status
        else:
            raise TypeError(f"Expected str for payment_status, got {type(payment_status).__name__}.")
        if type(fulfillment_status) is str:
            self._dict["fulfillment_status"] = fulfillment_status
        else:
            raise TypeError(f"Expected str for fullfillment_status, got {type(fulfillment_status).__name__}.")
        if type(total) is str or type(total) is float:
            self._dict["total"] = total
        else:
            raise TypeError(f"Expected str or float for total, got {type(total).__name__}.")
    
    def __getitem__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            return