"""
Hello from Tools/Common/Input.py

Functions:
    GetInteger
        It requires users to enter integers in a range.
    Demo
        This function is a demo of all functions and classes in this module.
"""


def GetInteger(prompt="Please enter a number:",
               lowerbound=0, upperbound=99,
               smaller_prompt="It's Smaller, please re-enter:",
               bigger_prompt="It's Bigger, please re-enter:",
               not_int_prompt="You did not enter a number, please re-enter:"):
    """
    It requires users to enter integers in a range.

    Parameters
    ----------
    prompt: str
        It is a prompt before users enters it.
    lowerbound: int
        The smallest integer that users can enter.
    upperbound: int
        The biggest integer that users can enter.
    smaller_prompt: str
        It's tips given when the integer entered by users is small.
    bigger_prompt: str
        It's tips given when the integer entered by users is big.
    not_int_prompt: str
        It's tips given when users' input is not an integer.

    Returns
    -------
    int
        It's an user-entered, within-range integer.
    """
    user_input = input(prompt)

    def InternalFunc1(num):
        while True:
            try:
                return int(num)
            except ValueError:
                num = input(not_int_prompt)
    result = InternalFunc1(user_input)

    while not lowerbound <= result <= upperbound:
        if result < lowerbound:
            user_input = input(smaller_prompt)
            result = InternalFunc1(user_input)
        if upperbound < result:
            user_input = input(bigger_prompt)
            result = InternalFunc1(user_input)
    return result


def Demo():
    """This function is a demo of all functions in this module."""
    print("Users input:", GetInteger())
    print("Users input:", GetInteger(lowerbound=-3, upperbound=10))
    input("Please press <Enter> to exit the demo.")


if __name__ == '__main__':
    Demo()
