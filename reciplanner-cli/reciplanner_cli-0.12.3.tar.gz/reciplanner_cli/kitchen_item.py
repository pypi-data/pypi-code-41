"""Module that contains the Item class

Classes
-------
Item
    A class used to store data about items in the kitchen, such as milk.
"""
import datetime

class Item:

    """Class for containing information about items in the kitchen, such as milk, condiments, etc."""

    def __init__ (self, name, amount, unit="units", categories=None, location=None, expiry_date = None, barcode=None):
        """Initializes an Item instance
        Arguments
        ---------
            name : string
                the name of the object itself, such as "Eggs"
            amount : float/int
                the amount of the item. In the eggs example, a carton of a dozen eggs would have amount = 12
            unit (optional) : pint unit
                the unit that the item is measured in. See the "pint" library for details.
            categories (optional) : list of strings
                the classification of the food. For eggs, this could be "animal product," or "protein food"
            location (optional) : string
                the location of the item in the kitchen. It can be "left cabinet", or "fridge"
            expiry_date (optional) : datetime.date
                the expiration date of an item
            barcode (optional) : int
                a barcode that represents the object **HAS NOT YET BEEN IMPLEMENTED**
        """

        self.name = name
        self.amount = amount
        self.unit = unit
        self.categories = categories
        self.location = location
        self.expiry_date = expiry_date
        self.barcode = barcode


    def get_description(self):
        """Returns a description of the item in a user-friendly format

        Returns
        -------
        string
            Description of the item, based on its attributes
        """

        item_str = []
        amt = 0.0
        if type(self.amount) == float and self.amount.is_integer():
            amt = str(int(self.amount))
        else:
            amt = self.amount
        item_str += str(amt)
        item_str += " "

        if self.unit != "units":
            item_str += str(self.unit)
            item_str += " of "

        item_str += self.name

        if self.location:
            item_str += " in the "
            item_str += self.location

        if self.expiry_date:
            now = datetime.date.today()
            time_until_expiry = self.expiry_date - now

            if time_until_expiry.days <= 0:
                item_str += " !== EXPIRED ==!"
            elif time_until_expiry.days <= 7:
                item_str += " - expires in "
                item_str += str(time_until_expiry.days)
                item_str += " days"

        return "".join(item_str)

    def set_amount(self, amount, ureg=None, unit=None):
        """Sets the amount to the amount specified

        Arguments
        ---------
        amount : float/int
            The numeric amount of the item, not including units
        ureg (optional) : pint.UnitRegistry
            The UnitRegistry used for unit conversions
        unit : pint unit
            THe unit to set the amount to
        """

        if unit and ureg:
            amt = amount * unit
            amt = amt.to_compact()

            self.amount = amt.magnitude
            self.unit = amt.units
        else:
            self.amount = amount

    def add_amount(self, amount, ureg=None, unit=None):
        """Adds the specified amount to the item's value. Supports differing units, as long as conversion is possible

        Arguments
        ---------
        amount : float/int
            The numeric amount of the item, not including units
        ureg (optional) : pint.UnitRegistry
            The UnitRegistry used for unit conversions
        unit : pint unit
            The unit of the amount to be added
        """

        if unit and self.unit and ureg:
            amt = ureg(str(self.amount) + " " + str(self.unit))
            to_add = amount * unit
            amt += to_add
            amt = amt.to_compact()

            self.amount = amt.magnitude
            self.unit = amt.units
        else:
            self.amount += amount

    def remove_amount(self, amount, ureg, unit=None):
        """Removes the specified amount from the item's amount

        Arguments
        ---------
        amount : float/int
            The numeric amount of the item, not including units
        ureg (optional) : pint.UnitRegistry
            The UnitRegistry used for unit conversions
        unit : pint unit
            The unit of the amount to be removed
        """

        if unit and self.unit:
            amt = ureg(str(self.amount) + " " + str(self.unit))
            to_remove = amount * unit
            amt -= to_remove
            amt = amt.to_compact()

            self.amount = amt.magnitude
            self.unit = amt.units
        else:
            self.amount -= amount

    def empty(self):
        """Sets the amount of the item to 0."""

        self.amount = 0
