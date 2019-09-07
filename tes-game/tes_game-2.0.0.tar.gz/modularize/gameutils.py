
import random

def weighted_random_selection(obj1, obj2):
    """Randomly select between two objects based on assigned 'weight'

    .. todo:: How about creating a utility module for common functionality?
    """
    weighted_list = 3 * [id(obj1)] + 7 * [id(obj2)]
    selection = random.choice(weighted_list)

    if selection == id(obj1):
        return obj1

    return obj2


def print_bold(msg, end='\n'):
    print("\033[1m" + msg + "\033[0m", end=end)