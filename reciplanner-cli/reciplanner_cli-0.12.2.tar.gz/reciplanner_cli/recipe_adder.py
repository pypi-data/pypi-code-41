"""Module that allows for adding new recipes and converting units in recipes

Methods
---------
convert_to_preferred(ingredients, ureg)
    converts the list of ingredients it was passed to metric units, and returns the modified list.

add_new_recipe(ureg, provided_ingredients=None)
    processes ingredients as strings into Item objects
"""
import collections
import re
import pint
import recipe
import kitchen_item

class NoAmountError(Exception):
    """Error raised when no amount is provided in a string to be parsed as an ingredient."""

    pass

#The density of butter is 959.47 grams / liter")
DENSITY_OF_BUTTER = 959.47

def convert_to_preferred(ingredients, ureg):
    """Converts the units for the list of ingredients to the metric system

    Arguments
    ---------
    ingredients: a list of Item objects that are the ingredients to be converted
    ureg: A UnitRegistry object to be used for conversions

    Returns
    -------
    list
        a list of the ingredients, with units converted to their metric counterparts.

    Special Cases
    -------------
    butter
        butter is always converted to a unit of mass, such as grams.
    """

    units = [x.unit for x in ingredients]
    imperial_units = dir(ureg.sys.imperial)
    i = 0
    for unit in units:
        new = 0
        if unit == "unit" or unit == "units":
            i += 1
            continue
        #Converts butter to grams, because butter should always be measured in grams
        elif "butter" in ingredients[i].name.lower():
            q = ingredients[i].amount * unit
            if ureg.liter in ureg.get_compatible_units(unit) and ureg.gram not in ureg.get_compatible_units(unit):
                new = (q.to(ureg.liter).magnitude * DENSITY_OF_BUTTER) * ureg.gram
            else:
                new = q.to(ureg.gram).to_compact()
        #These items are liquid units. If they aren't dealt with on their own, they cause problems with the conversion
        elif unit in [ureg.liquid_cup, ureg.liquid_pint, ureg.liquid_quart, ureg.liquid_gallon, ureg.tablespoon, ureg.teaspoon, ureg.fluid_ounce]:
            q = ingredients[i].amount * unit
            if q.to(ureg.milliliter).magnitude > 100:
                new = q.to(ureg.deciliter)
            else:
                new = q.to(ureg.milliliter)
        else:
            compatible_units = ureg.get_compatible_units(unit)
            preferred_units = [ureg.milliliter, ureg.gram]
            q = ingredients[i].amount * unit
            for u in preferred_units:
                if u == ureg.milliliter and ureg.liter in compatible_units:
                    #If converting to millililters would make it over 100 milliliters, convert it to deciliters instead
                    if q.to(ureg.milliliter).magnitude > 100:
                        new = q.to(ureg.deciliter)
                    else:
                        new = q.to(ureg.milliliter)
                    break
                else:
                    try:
                        new = q.to(u)
                    except Exception:
                        new = q.to_base_units()
        ingredients[i].unit = new.units
        ingredients[i].set_amount(round(new.magnitude, 2))
        i += 1
    return ingredients



def add_new_recipe(ureg, provided_ingredients=None):
    """Processes the addition of a new recipe. Accepts items line by line, or as a list

        Format
        ------
        User input in the following formats
        <amount> <unit> of <substance>
        <amount> <unit> <substance>
        <amount> <substance>
        Example: "2 cups of butter"
        If a unit is not specified, it will be set to the string "units"
        Returns a list composed of Item objects which represent the ingredients

        Arguments
        ---------
        ureg: The UnitRegistry object that contains the units
        provided_ingredients (optional): A list of strings to be parsed as ingredients. Follows the same format specified above.

        Returns
        -------
        list
            a list of Item objects that matches the items described in the strings.
        -1
            returns -1 if there was an error parsing one of the ingredients in provided_ingredients
    """

    #An OrderedDict of all units recognized. Can be expanded at any time if you choose to.
    units = collections.OrderedDict([
        ("\\bpounds?\\b|\\blbs?\\b", ureg.pound),
        ("\\bounces?\\b|\\boz.?\\b", ureg.ounce),
        ("\\bcups?\\b", ureg.liquid_cup),
        ("\\bpints?\\b", ureg.liquid_pint),
        ("\\bquarts?\\b", ureg.liquid_quart),
        ("\\bgallons?\\b", ureg.liquid_gallon),
        ("\\bliters?\\b|\\bl\\b", ureg.liter),
        ("\\bmilliliters?\\b|\\bml\\b", ureg.milliliter),
        ("\\bdeciliters?\\b|\\bdl\\b", ureg.deciliter),
        ("\\bmilligrams?\\b|\\bmg\\b", ureg.gram),
        ("\\bgrams?\\b|\\bg\\b", ureg.gram),
        ("\\bkilograms?\\b|\\bkg\\b", ureg.kilogram),
        ("\\bdecigrams?\\b|\\bdg\\b", ureg.decigram),
        ("\\bfluid ounces?\\b|\\bfl oz.?\\b", ureg.fluid_ounce),
        ("\\btable ?spoons?\\b|\\btbps\\b", ureg.tablespoon),
        ("\\btea ?spoons?\\b|\\btps\\b", ureg.teaspoon),
        ("\\bfoot\\b|\\bfeet\\b|\\bft\\b", ureg.foot),
        ("\\binche?s?\\b|\\bin.?\\b", ureg.inch),
        ("\\bcentimeters?|\\bcm.?\\b", ureg.centimeter),
        ("\\bmeters?|\\bm.?\\b", ureg.meter)
    ])
    if provided_ingredients:
        ingredients = []
        for k in provided_ingredients.split("\n"):
            if k == "\n" or len(k) <= 0:
                continue
            amount = 0
            unit = "units"
            substance = ""

            #Find and store the number in the string even if they have a comma, or are written in scientific notation
            amt_occurrence = re.search("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", k)
            if amt_occurrence:
                amount = k[amt_occurrence.start():amt_occurrence.end()]
                amount = amount.replace(",", "")
                amount = float(amount)
            else:
                raise NoAmountError("No amount was provided.")

            #Identify the unit and store its location in the string
            unit_match = 0
            for u in units:
                unit_match = re.search(u, k)
                if unit_match:
                    unit = units[u]
                    break

            if unit_match:
                substance = k[unit_match.end():].strip()
            else:
                substance = k[amt_occurrence.end():].strip()

            match = re.search("\\bof\\b", k)
            if match:
                substance = k[match.end() + 1:]

            ingredients.append(kitchen_item.Item(substance, amount, unit))
        return ingredients
    else:
        print("What's the recipe call for, puncy? Type \"exit\" when you're finished, or just press <Enter> on an empty line.")
        k = ""
        ingredients = []
        while k.lower() != "exit" and k.lower() != "quit":
            k = input("")
            if k.lower() == "exit" or k.lower() == "quit" or not k:
                break
            amount = 0
            unit = "units"
            substance = ""

            #Find and store the number in the string even if they have a comma, or are written in scientific notation
            amt_occurrence = re.search("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", k)
            if amt_occurrence:
                amount = k[amt_occurrence.start():amt_occurrence.end()]
                amount = amount.replace(",", "")
                amount = float(amount)
            else:
                print("Please add a quantity and try again")
                k = input("")
                continue

            #Identify the unit and store its location in the string
            unit_match = 0
            for u in units:
                unit_match = re.search(u, k)
                if unit_match:
                    unit = units[u]
                    break

            if unit_match:
                substance = k[unit_match.end():].strip()
            else:
                substance = k[amt_occurrence.end():].strip()

            match = re.search("\\bof\\b", k)
            if match:
                substance = k[match.end() + 1:]

            ingredients.append(kitchen_item.Item(substance, amount, unit))
        return ingredients
