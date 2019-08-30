# Created by MysteryBlokHed in 2019.
class Product(object):
    def __init__(self, name, image, product_url, price, review_score, review_count):
        self._dict = {}
        
        # Type checking
        if type(name) is str:
            self._dict["name"] = name
        else:
            raise TypeError(f"Expected str for name, got {type(name).__name__}.")
        if type(image) is str:
            self._dict["image"] = image
        else:
            raise TypeError(f"Expected str for image, got {type(image).__name__}.")
        if type(product_url) is str:
            self._dict["product_url"] = product_url
        else:
            raise TypeError(f"Expected str for product_url, got {type(product_url).__name__}.")
        if type(price) is str:
            self._dict["price"] = price
        else:
            raise TypeError(f"Expected str for price, got {type(price).__name__}.")
        if type(review_score) is float or type(review_score) is type(None):
            self._dict["review_score"] = review_score
        else:
            raise TypeError(f"Expected float or NoneType for review_score, got {type(review_score).__name__}.")
        if type(review_count) is str or type(review_count) is int or type(review_count) is type(None):
            self._dict["review_count"] = review_count
        else:
            raise TypeError(f"Expected str, int, or NoneType for review_count, got {type(review_count).__name__}.")
    
    def __getitem__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            return