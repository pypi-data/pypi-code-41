
import random

class NumberGuesser:
    def __init__(self, difficulty='low'):
        if difficulty == 'low':
            self.max = 10

        elif difficulty == 'medium':
            self.max = 20

        elif difficulty == 'high':
            self.max = 30

    def start(self):
        """Starts number guesser game"""
        solution = random.randint(0,self.max)
        game_over = False
        attempts = 0

        while not game_over:
            try:
                guess = input("Make a guess ({0} - {1}): ".format(0, self.max))

                if float(guess) - int(guess) > 0:
                    raise Exception
            except Exception:
                print("Please make sure the guess is of correct type (integer).")
                print("Try again")
                continue

            guess = int(guess)
            attempts += 1
            if solution < guess:
                print("It's lower")
            elif solution > guess:
                print("It's higher")
            else:
                game_over = True
                print ("Got it")
                print ("Number of Attempts until getting solution: {0}".format(attempts))

        print ("Game Over! Thank you for playing.")

if __name__ == '__main__':
    difficulty = input("Choose difficulty (low, medium, high): ")
    game = NumberGuesser(difficulty)
    game.start()