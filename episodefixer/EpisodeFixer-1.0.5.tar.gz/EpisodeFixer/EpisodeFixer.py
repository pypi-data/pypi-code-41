#!/usr/bin/env python3

from .TVShow import TVShow

def main():
    """The main function. It involves creating TVShow class and running rename method on it.
    """
    tvshow = TVShow()
    tvshow.rename()

# This is the driver code where we call the main function.
if __name__ == "__main__":
    main() 