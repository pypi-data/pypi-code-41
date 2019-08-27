"""The central module that contains all of the functions for the user interface

Classes
-------
KitchenManager
    A class used to interact with the user, provide menus, and save/load recipes/ingredients.
"""
import recipe_adder
import kitchen_item
import pint
import sys
from pathlib import Path
import os
import recipe
import pickle
import tkinter as tk
from threading import Thread
import datetime

class KitchenManager:
    """Class for containing the KitchenManager instance. Used to interact with the user, provide menus, and save/load recipes/ingredients

    ...

    Attributes
    ----------
    keep_going : bool
        a boolean that controls whether or not to continue the main loop. set to false to quit the program
    textbox_text : string
        a variable that contains the text from the textbox created when editing steps/ingredients/categories

    """

    keep_going = True
    textbox_text = None

    def print_options(self):
        """Prints the options for the main menu"""

        print("Reciplanner")
        print("=" * len("Reciplanner"))
        print("0. Add new recipe")
        print("1. Change previous recipe")
        print("2. Remove a recipe")
        print("3. View recipes")
        print("4. What's in my kitchen?")
        print("5. Add new item to kitchen")
        print("6. Remove item from kitchen")
        print("7. Forget item from kitchen")
        print("8. Edit an item in the kitchen")
        print("9. Quit")

    def prompt_add_recipe(self):
        """Prompts the user to add a recipe"""

        name = input("Recipe name: ")
        ingredients = recipe_adder.add_new_recipe(self.ureg)
        print("Attempting to convert ingredients to metric units...")
        try:
            new_ingredients = recipe_adder.convert_to_preferred(ingredients[:], self.ureg)
            ingredients = new_ingredients
        except Exception as e:
            print("An issue occurred during conversion. Ingredients unchanged.")
            print(e)
        else:
            print("Successfully converted ingredient units.")
        do_steps = input("Would you like to list steps?").lower()
        steps = None
        if do_steps == "yes" or do_steps == "y":
            print("Type your steps one by one, and when you're finished, type 'exit', or just press <Enter> on a blank line.")
            i = 1
            steps = []
            k = input("Step " + str(i) + ": ")
            while k.lower() != "exit" and k.lower() != "quit" and k.lower():
                steps.append(k)
                i += 1
                k = input("Step " + str(i) + ": ")
        new_recipe = None
        new_recipe = recipe.Recipe(name, ingredients, steps)
        self.recipes.append(new_recipe)
        self.save_recipes()
        print("Recipe successfully added.")

    def textbox_prompt(self, arr, type=None):
        """Creates an editable textbox with the ingredients/steps/categories that it's passed

        Arguments
        ---------
        arr : list
            List to display in the textbox. Can either be a list of Items, or a list of strings.
            If it's a list of Items, set the type variable to "ingredients." Otherwise, it can just be left blank.
            By default, it is processed as if it were a list of strings, with each string on its own line.

        type (optional) : string
            The type of list that has been passed as the 'arr' argument. Set to "ingredients" if
            you're passing it a list of Items to be parsed as ingredients. Otherwise, leave it blank.

        Side effects
        ------------
        Sets the textbox_text variable to the edited text from the textbox

        """

        root = tk.Tk()
        root.geometry("500x500")
        textbox = tk.Text(root)
        text_to_put = []
        if type == "ingredients":
            for ingr in arr:
                if ingr.unit != "units":
                    if ingr.amount.is_integer():
                        text_to_put.append(str(int(ingr.amount)) + " " + str(ingr.unit) + " of " + str(ingr.name))
                    else:
                        text_to_put.append(str(ingr.amount) + " " + str(ingr.unit) + " of " + str(ingr.name))
                else:
                    if ingr.amount.is_integer():
                        text_to_put.append(str(int(ingr.amount)) + " " + str(ingr.name))
                    else:
                        text_to_put.append(str(ingr.amount) + " " + str(ingr.name))
        else:
            text_to_put = arr
        textbox.delete(1.0, tk.END)
        if text_to_put:
            for line in text_to_put:
                textbox.insert(tk.END, line + "\n")
            text_to_put = "".join(text_to_put)

        def do_finish():
            """Function that sets the textbox_text variable to the textbox's text, and closes the textbox window"""

            if type == "ingredients":
                self.textbox_text = textbox.get(1.0, tk.END)[:-1]
            else:
                self.textbox_text = textbox.get(1.0, tk.END)[:-1].split("\n")
            root.destroy()

        textbox.pack()
        save_button = tk.Button(root, text="Save & Exit", command=do_finish)
        save_button.pack()
        root.mainloop()


    def prompt_what_to_change_in_recipe(self, recipe):
        """Prompts the user for what exactly in the recipe they want to change

        Arguments
        ---------
        recipe : Recipe
            Recipe object to be modified

        Returns
        -------
        Recipe
            The modified recipe that was passed as an argument
        """

        if recipe:
            while True:
                print("What would you like to change?")
                print("0. Name")
                print("1. Ingredients")
                print("2. Steps")
                print("3. Quit")
                to_change = input(":").lower()
                if to_change.isdigit() and int(to_change) <= 3:
                    to_change = int(to_change)
                    if to_change == 0:
                        try:
                            print("Current name:", recipe.name)
                        except AttributeError:
                            print("Current name: ERROR - CORRUPTED RECIPE")
                        recipe.name = input("New name: ")
                        return recipe
                    elif to_change == 1:
                        new_ingredients = None
                        while True:
                            self.textbox_prompt(recipe.ingredients, "ingredients")
                            print(self.textbox_text)
                            new_ingredients = self.textbox_text
                            try:
                                new_ingredients = recipe_adder.add_new_recipe(self.ureg, new_ingredients)
                                new_ingredients = recipe_adder.convert_to_preferred(new_ingredients, self.ureg)
                            except recipe_adder.NoAmountError:
                                print("There was no amount provided for one of your ingredients. Please try again.")
                            else:
                                break
                        recipe.ingredients = new_ingredients
                        print("Ingredients successfully changed.")
                        return recipe
                    elif to_change == 2:
                        self.textbox_prompt(recipe.steps)
                        new_steps = self.textbox_text
                        recipe.steps = new_steps
                        print("Steps successfully changed.")
                        return recipe
                    elif to_change == 3:
                        break
                else:
                    print("Invalid input. Try again")
        else:
            print("This recipe has been corrupted. It is not possible to edit this recipe.")


    def prompt_change_recipe(self):
        """Prompts the user for which recipe they would like to change"""

        if len(self.recipes) > 0:
            for i in range(len(self.recipes)):
                try:
                    print(str(i) + ".", self.recipes[i].name)
                except AttributeError:
                    print(str(i) + ". ERROR - CORRUPTED RECIPE")
            print(str(i + 1) + ". Cancel")
            print("Which recipe would you like to change?")
            to_change = input(": ")
            if to_change.isdigit() and int(to_change) <= len(self.recipes) - 1:
                self.recipes[int(to_change)] = self.prompt_what_to_change_in_recipe(self.recipes[int(to_change)])
                self.save_recipes()
            elif to_change.isdigit() and int(to_change) == (i + 1):
                return None
            else:
                print("Invalid input. Try again")
        else:
            print("You have no recipes.")

    def prompt_remove_recipe(self):
        """Prompts the user for which recipe to remove, and deletes it."""

        if len(self.recipes) > 0:
            for i in range(len(self.recipes)):
                try:
                    print(str(i) + ".", self.recipes[i].name)
                except AttributeError:
                    print(str(i) + ". ERROR - CORRUPTED RECIPE")
            print(str(i + 1) + ". Cancel")
            print("Which recipe would you like to remove?")
            to_remove = input(": ")
            if to_remove.isdigit() and int(to_remove) <= len(self.recipes) - 1:
                self.recipes.pop(int(to_remove))
                self.save_recipes()
                print("Recipe removed.")
            elif to_remove.isdigit() and int(to_remove) == (i + 1):
                return None
            else:
                print("Invalid input. Try again")
        else:
            print("You have no recipes.")

    def prompt_view_recipes(self):
        """Prompts the user which recipe they would like to view, displays it, and displays which ingredients the user is missing - if any."""

        if len(self.recipes) > 0:
            for i in range(len(self.recipes)):
                try:
                    print(str(i) + ".", self.recipes[i].name)
                except AttributeError:
                    print(str(i) + ". ERROR - CORRUPTED RECIPE")
            print(str(i + 1) + ". Cancel")
            print("Which recipe would you like to view?")
            to_view = input(":")
            if to_view.isdigit() and int(to_view) == (i + 1):
                return None
            if to_view.isdigit() and int(to_view) <= len(self.recipes) - 1 and self.recipes[int(to_view)]:
                self.recipes[int(to_view)].print_recipe()
                can_make, ingredients_missing, amount_missing = self.recipes[int(to_view)].can_make(self.kitchen, self.ureg)
                if can_make:
                    print("Good news! You have all the ingredients you need to make", self.recipes[int(to_view)].name)
                else:
                    print("You're missing the following ingredients")
                    print("=" * len("You're missing the following ingredients"))
                    for ingr, amt in zip(ingredients_missing, amount_missing):
                        if type(amt) == float or type(amt) == int:
                            if type(amt) == float and amt.is_integer():
                                print(int(amt), ingr)
                            else:
                                print(amt, ingr)
                        else:
                            if type(amt.magnitude) == float and amt.magnitude.is_integer():
                                print(int(amt.magnitude), amt.units, "of", ingr)
                            else:
                                print(amt, amt.units, "of", ingr)
            elif self.recipes[int(to_view)] == None:
                print("This recipe has been corrupted. It is unable to be displayed.")
            else:
                print("Invalid input. Try again")
        else:
            print("You have no recipes.")

    def prompt_whats_in_my_kitchen(self):
        """Displays the items in the user's kitchen, sorted by category. Does not display items if their amount == 0"""

        if len(self.kitchen) > 0:
            categories = {
            "unsorted": []
            }

            for item in self.kitchen:
                description = item.get_description()
                if item.amount > 0:
                    if item.categories:
                        for category in item.categories:
                            if category not in categories:
                                categories[category] = []
                            categories[category].append(description)
                    else:
                        categories["unsorted"].append(description)

            for category in categories:
                if categories[category]:
                    print(category.upper())
                    print("=" * len(category))
                    for description in categories[category]:
                        print(description)
                    print("\n")
        else:
            print("Your kitchen is empty.")


    def prompt_add_new_item_to_kitchen(self):
        """Prompts the user to add a new item to their kitchen. Only the name and amount are required."""

        print("Please fill out the following information.")
        print("If an item is starred, you must fill it out. If it is not starred, you can just press ENTER to skip it.")

        name = None
        while not name:
            name = input("Name (*): ").lower()

        amount = None
        unit = "units"
        while (not amount) and type(amount) != float and type(amount) != pint.quantity:
            amount = input("Amount (*): ")
            if amount.isdigit():
                try:
                    amount = float(amount)
                except ValueError:
                    print('"' + str(amount) + '"', "is not a number. Please try again.")
            else:
                try:
                    q = self.ureg.parse_expression(amount)
                    amount = q.magnitude
                    unit = q.units
                except:
                    print("There was an issue with your input. Please try again.")

        new_item = kitchen_item.Item(name, amount)
        if unit != "units":
            new_item.unit = unit

        all_item_names = [x.name for x in self.kitchen]
        if name in all_item_names:
            index = all_item_names.index(name)
            if unit != "units":
                self.kitchen[index].add_amount(amount, self.ureg, unit)
            else:
                self.kitchen[index].add_amount(amount, self.ureg)
            self.save_kitchen()
            print("Successfully added your item to your kitchen.")
            return None

        categories = []
        i = 1
        category = input("Category " + str(i) + ": ")
        if category:
            while True:
                if category.lower() == "exit" or category.lower() == "cancel" or not category:
                    break
                categories.append(category.lower())
                i += 1
                category = input("Category " + str(i) + ": ")

        if categories:
            new_item.categories = categories

        location = input("Location: ").lower()

        if location:
            new_item.location = location

        expiry_date = input("Expiration date (DD/MM/YYYY): ")
        if expiry_date:
            while True:
                if expiry_date.lower() == "exit" or expiry_date.lower() == "cancel" or not expiry_date:
                    break
                try:
                    expiry_date = datetime.datetime.strptime(expiry_date, "%d/%m/%Y").date()
                except:
                    print("Please enter the date in the DD/MM/YYYY format, with no parenthesis.")
                else:
                    break
                expiry_date = input("Expiration date (DD/MM/YYYY): ")

        if expiry_date:
            new_item.expiry_date = expiry_date

        self.kitchen.append(new_item)
        self.save_kitchen()
        print("New item successfully added.")

    def prompt_what_to_change_in_item(self, item):
        """Prompts the user for what to change in a specific item

        Arguments
        ---------
        item : Item
            The Item object to be modified

        Returns
        -------
        Item
            The modified variant of the Item object that was passed as an argument
        """

        if item:
            while True:
                print("What would you like to change?")
                print("0. Name")
                print("1. Amount")
                print("2. Location")
                print("3. Categories")
                print("4. Expiration date")
                print("5. Cancel")
                to_change = input(":").lower()
                if to_change.isdigit() and int(to_change) <= 5:
                    to_change = int(to_change)
                    if to_change == 0:
                        new_name = input("New name: ").lower()
                        item.name = new_name
                        print("Successfully changed the name of your item.")
                        return item
                    elif to_change == 1:
                        while True:
                            amt = input("New amount: ").lower()
                            try:
                                amt = self.ureg.parse_expression(amt)
                            except:
                                if amt.isdigit():
                                    item.set_amount(float(amt))
                                    print("Successfully edited the amount of your item")
                                    break
                                else:
                                    print("There was a problem with your input. Please try again.")
                            else:
                                item.set_amount(amt.magnitude, self.ureg, amt.units)
                                print("Successfully edited the amount of your item")
                                break
                        return item
                    elif to_change == 2:
                        new_location = input("New location: ").lower()
                        item.location = new_location
                        print("Successfully changed the location of your item.")
                        return item
                    elif to_change == 3:
                        self.textbox_prompt(item.categories)
                        new_categories = self.textbox_text
                        item.categories = new_categories
                        return item
                    elif to_change == 4:
                        expiry_date = None
                        while True:
                            expiry_date = input("Expiration date (DD/MM/YYYY): ")
                            try:
                                expiry_date = datetime.datetime.strptime(expiry_date, "%d/%m/%Y").date()
                            except:
                                print("Please enter the date in the DD/MM/YYYY format, with no parenthesis.")
                            else:
                                break
                        item.expiry_date = expiry_date
                        print("Successfully changed the expiration date of your item.")
                        return item
                    elif to_change == 5:
                        break
                else:
                    print("Invalid input. Try again")
        else:
            print("This item has been corrupted. It is not possible to edit this recipe.")

    def prompt_edit_an_item(self):
        """Prompts the user for which item they want to edit"""

        if len(self.kitchen) > 0:
            for i in range(len(self.kitchen)):
                try:
                    print(str(i) + ".", self.kitchen[i].name)
                except AttributeError:
                    print(str(i) + ". ERROR - CORRUPTED ITEM")
            print(str(i + 1) + ". Cancel")
            print("Which item would you like to edit?")
            to_change = input(": ")
            if to_change.isdigit() and int(to_change) <= len(self.kitchen) - 1:
                self.kitchen[int(to_change)] = self.prompt_what_to_change_in_item(self.kitchen[int(to_change)])
                self.save_kitchen()
            elif to_change.isdigit() and int(to_change) == (i + 1):
                return None
            else:
                print("Invalid input. Try again")
        else:
            print("Your kitchen is empty.")


    def prompt_how_much_to_remove(self, index):
        """Prompts the user for how much of the item specified they wish to remove.
        It does not delete the item - it only sets its amount to 0.

        Arguments
        ---------
        index : int
            Integer that represents the index of the item in the self.kitchen list
        """

        print(self.kitchen[index].get_description())
        print("How much would you like to remove?")
        print('You can enter a certain amount (ex: 2 kg), type "all", or "cancel".')
        amt = input(": ").lower()
        if amt != "all":
            while True:
                try:
                    amt = self.ureg.parse_expression(amt)
                except:
                    if amt.isdigit():
                        self.kitchen[index].remove_amount(float(amt), self.ureg)
                        print("Successfully removed", amt, "from your supply of", self.kitchen[index].name + ".")
                        break
                    else:
                        print("There was a problem with your input. Please try again.")
                else:
                    self.kitchen[index].remove_amount(amt.magnitude, self.ureg, amt.units)
                    print("Successfully removed", amt.magnitude, amt.units, "from your supply of", self.kitchen[index].name + ".")
                    break
        elif amt == "cancel" or amt == "quit":
            return None
        else:
            self.kitchen[index].empty()
            print("Successfully emptied your supply of", self.kitchen[index].name + ".")
        self.save_kitchen()


    def prompt_remove_item_from_kitchen(self):
        """Prompts the user for which item they would like to remove from the kitchen
        It does not delete the item - it only sets its amount to 0.
        """

        if len(self.kitchen) > 0:
            for i in range(len(self.kitchen)):
                try:
                    print(str(i) + ".", self.kitchen[i].name)
                except AttributeError:
                    print(str(i) + ". ERROR - CORRUPTED ITEM")
            print(str(i + 1) + ". Cancel")
            print("Which item would you like to remove?")
            to_remove = input(": ")
            if to_remove.isdigit() and int(to_remove) <= len(self.kitchen) - 1:
                self.prompt_how_much_to_remove(int(to_remove))
                self.save_kitchen()
            elif to_remove.isdigit() and int(to_remove) == (i + 1):
                return None
            else:
                print("Invalid input. Try again")
        else:
            print("Your kitchen is empty.")

    def prompt_forget_item_from_kitchen(self):
        """Prompts the user for which item they would like to forget, and deletes all of its data."""

        if len(self.kitchen) > 0:
            for i in range(len(self.kitchen)):
                try:
                    print(str(i) + ".", self.kitchen[i].name)
                except AttributeError:
                    print(str(i) + ". ERROR - CORRUPTED ITEM")
            print(str(i + 1) + ". Cancel")
            print("Which item would you like me to forget?")
            to_forget = input(": ")
            if to_forget.isdigit() and int(to_forget) <= len(self.kitchen) - 1:
                self.kitchen.pop(int(to_forget))
                self.save_kitchen()
                print("Item forgotten.")
            elif to_forget.isdigit() and int(to_forget) == (i + 1):
                return None
            else:
                print("Invalid input. Try again")
        else:
            print("Your kitchen is empty.")

    def close_program(self):
        """Closes the program safely"""

        self.save_recipes()
        self.keep_going = False

    def load_recipes(self):
        """Loads the saved recipes if there are any. If there aren't, it creates the file."""

        directory = None
        recipes_file = None
        if sys.platform == "win32":
            directory = str(Path.home()) + "\\AppData\\Local\\Reciplanner"
            recipes_file = Path(directory + "\\recipes")
        elif sys.platform == "darwin":
            directory = str(Path.home()) + "/Library/Preferences/Reciplanner"
            recipes_file = Path(directory + "/recipes")
        else:
            directory = str(Path.home()) + "/.config/reciplanner"
            recipes_file = Path(directory + "/recipes")
        if not os.path.exists(directory):
            os.makedirs(directory)
        val = []
        try:
            with open(recipes_file, 'rb') as recipes_file_opened:
                val = pickle.load(recipes_file_opened)
        except FileNotFoundError:
            with open(recipes_file, 'wb') as recipes_file_opened:
                pickle.dump([], recipes_file_opened)
        return val

    def save_recipes(self):
        """Saves the recipes. Creates a file to store the recipes if it doesn't already exist."""

        directory = None
        recipes_file = None
        if sys.platform == "win32":
            directory = str(Path.home()) + "\\AppData\\Local\\Reciplanner"
            recipes_file = Path(directory + "\\recipes")
        elif sys.platform == "darwin":
            directory = str(Path.home()) + "/Library/Preferences/Reciplanner"
            recipes_file = Path(directory + "/recipes")
        else:
            directory = str(Path.home()) + "/.config/reciplanner"
            recipes_file = Path(directory + "/recipes")
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(recipes_file, 'wb') as recipes_file_opened:
            pickle.dump(self.recipes, recipes_file_opened)

    def load_kitchen(self):
        """Loads the items in the user's kitchen from the kitchen file, if it exists. Creates it if it doesn't."""

        directory = None
        kitchen_file = None
        if sys.platform == "win32":
            directory = str(Path.home()) + "\\AppData\\Local\\Reciplanner"
            kitchen_file = Path(directory + "\\kitchen")
        elif sys.platform == "darwin":
            directory = str(Path.home()) + "/Library/Preferences/Reciplanner"
            kitchen_file = Path(directory + "/kitchen")
        else:
            directory = str(Path.home()) + "/.config/reciplanner"
            kitchen_file = Path(directory + "/kitchen")
        if not os.path.exists(directory):
            os.makedirs(directory)
        val = []
        try:
            with open(kitchen_file, 'rb') as kitchen_file_opened:
                val = pickle.load(kitchen_file_opened)
        except FileNotFoundError:
            with open(kitchen_file, 'wb') as kitchen_file_opened:
                pickle.dump([], kitchen_file_opened)
        return val

    def save_kitchen(self):
        """Saves the items in the user's kitchen to the kitchen file, if it exists. Creates it if it doesn't."""

        directory = None
        kitchen_file = None
        if sys.platform == "win32":
            directory = str(Path.home()) + "\\AppData\\Local\\Reciplanner"
            kitchen_file = Path(directory + "\\kitchen")
        elif sys.platform == "darwin":
            directory = str(Path.home()) + "/Library/Preferences/Reciplanner"
            kitchen_file = Path(directory + "/kitchen")
        else:
            directory = str(Path.home()) + "/.config/reciplanner"
            kitchen_file = Path(directory + "/kitchen")
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(kitchen_file, 'wb') as kitchen_file_opened:
            pickle.dump(self.kitchen, kitchen_file_opened)

    def __init__(self):
        """Initializes a KitchenManager object."""

        self.recipes = self.load_recipes()
        self.kitchen = self.load_kitchen()
        self.ureg = pint.UnitRegistry()
