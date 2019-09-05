def dict_depth(collection):
  if isinstance(collection, dict) and collection:
    return 1 + max(dict_depth(collection[a]) for a in collection)
  if isinstance(collection, list) and collection:
    return 1 + max(dict_depth(a) for a in collection)
  return 0
