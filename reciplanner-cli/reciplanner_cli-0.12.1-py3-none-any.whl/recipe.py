"""Module that allows for creating, modifying, and working with Recipe objects"""
class Recipe:
    """Objects of class 'Recipe' are recipes that contain ingredients, amounts, and steps."""

    def __init__ (self, name, ingredients, steps=None):
        """Initializes an object of class Recipe to store recipes

        Arguments
        ---------
            name : string
                the name of the recipe
            ingredients : list
                a list of Item objects that represent the ingredients in the recipe
            steps (optional) : list
                a list of strings that represent the steps
        """

        self.name = name
        self.ingredients = ingredients
        self.steps = steps

    def get_name(self):
        """Returns the name of the recipe if it exists, or "Unnamed recipe" if it does not"""

        if self.name:
            return self.name
        else:
            return "Unnamed recipe"

    def can_make(self, current_ingredients, ureg):
        """Returns a boolean indicating if the user has the ingredients to make a recipe, a list of the missing ingredients if there are any, and a list of how much is missing for each.

        Arguments
        ---------
            current_ingredients : list
                A list of the ingredients in the user's kitchen
            ureg : pint.UnitRegistry
                The UnitRegistry used for unit conversions

        Returns
        -------
        bool
            A boolean value indicating if the user can make the recipe with the current ingredients
        list
            A list of the ingredients that the user is missing. Indices in this list correspond to those in the next list.
        list
            A list of the amount of each ingredient that is missing. Indices in this list correspond to those in the previous list.
        """

        ingredients = self.ingredients
        ingredients_missing = []
        amount_missing = []
        for ingr in ingredients:
            nonzero_ingredient_names = [x.name for x in current_ingredients if x.amount > 0]
            nonzero_ingredients = [x for x in current_ingredients if x.amount > 0]
            if ingr.name in nonzero_ingredient_names:
                current_ingredient = nonzero_ingredients[nonzero_ingredient_names.index(ingr.name)]
                if ingr.unit == "units":
                    if ingr.amount > current_ingredient.amount:
                        ingredients_missing.append(ingr.name)
                        amount_missing.append(ingr.amount - current_ingredient.amount)
                else:
                    amount_of_current_ingredient = current_ingredient.amount * ureg(str(current_ingredient.unit))
                    amount_needed = ingr.amount * ureg(str(ingr.unit))
                    if amount_needed > amount_of_current_ingredient:
                        ingredients_missing.append(ingr.name)
                        amount_missing.append(amount_needed - amount_of_current_ingredient)
            else:
                ingredients_missing.append(ingr.name)
                if ingr.unit == "units":
                    amount_missing.append(ingr.amount)
                else:
                    amount_missing.append(ingr.unit * ingr.amount)
        return not bool(len(ingredients_missing)), ingredients_missing, amount_missing

    def print_recipe(self):
        """Prints the name of the recipe, its ingredients, and its steps (with appropriate numbers)."""

        print("Name:", self.name)
        for ingr in self.ingredients:
            if ingr.unit != "units":
                if ingr.amount.is_integer():
                    print(int(ingr.amount), ingr.unit, "of", ingr.name)
                else:
                    print(ingr.amount, ingr.unit, "of", ingr.name)
            else:
                if ingr.amount.is_integer():
                    print(int(ingr.amount), ingr.name)
                else:
                    print(ingr.amount, ingr.name)
        if self.steps:
            print("\nSteps")
            print("=" * len("Steps"))
            for i in range(len(self.steps)):
                print(str(i + 1) + ".", self.steps[i])
