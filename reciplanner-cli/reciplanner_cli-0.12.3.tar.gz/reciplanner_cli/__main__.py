"""Launches the Reciplanner program"""
from kitchen_manager import KitchenManager
km = KitchenManager()

while km.keep_going:
  km.print_options()
  k = input(":").lower()
  options = {
      0: km.prompt_add_recipe,
      1: km.prompt_change_recipe,
      2: km.prompt_remove_recipe,
      3: km.prompt_view_recipes,
      4: km.prompt_whats_in_my_kitchen,
      5: km.prompt_add_new_item_to_kitchen,
      6: km.prompt_remove_item_from_kitchen,
      7: km.prompt_forget_item_from_kitchen,
      8: km.prompt_edit_an_item,
      9: km.close_program
  }
  if k.isdigit() and int(k) <= len(options) - 1:
      options[int(k)]()
  else:
      print("Invalid input. Please try again")
  print("\n\n\n")
