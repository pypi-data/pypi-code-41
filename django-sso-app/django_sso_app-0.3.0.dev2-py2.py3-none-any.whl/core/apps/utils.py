import random
import string


def get_random_string(N):
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
