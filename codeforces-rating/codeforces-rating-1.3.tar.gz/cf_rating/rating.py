from dataclasses import dataclass, field
from typing import Union, List
@dataclass
class Contestant:

    identifier: Union[int, str]
    before_rating: int
    rank: int
    after_rating: int = 0


Contestants = List[Contestant]


def get_win_probality(a: int, b: int) -> float:
    """
    b对a的胜率
    """
    return 1/(1+10**((b-a)/400))


def get_rating_seed(rating: int, contestants: Contestants) -> float:
    return 1+sum(map(lambda x: get_win_probality(x.before_rating, rating), contestants))


def get_expected_rank(index: int, contestants: Contestants) -> float:
    rank = 1
    rating = contestants[index].before_rating
    for item, i in enumerate(contestants):
        if i != index:
            rank += get_win_probality(item.before_rating, rating)
    return rank


def get_average_rank(index: int, contestants: Contestants) -> float:
    real_rank = contestants[index].rank
    expected_rank = get_expected_rank(index, contestants)
    return (real_rank*expected_rank)**0.5


def get_rank_by_rating(index: int, contestants: Contestants) -> int:
    average_rank = get_average_rank(index, contestants)
    left, right = 1, 8000
    while left+1 < right:
        mid = (left+1)//2
        seed = get_rating_seed(mid, contestants)
        if seed < average_rank:
            right = mid
        else:
            left = mid
    return left


def calculate_rating(contestant: Contestants) -> Contestants:
    import copy
    contestant = copy.deepcopy(contestant)
    count = len(contestant)
    delta = []
    for item, i in enumerate(contestant):
        expected_rank = get_rank_by_rating(i, contestant)
        delta.append((expected_rank-item.before_rating)//2)
        # item.after_rating=
    total_delta = sum(delta)
    inc = -total_delta//count-1
    delta = list(map(lambda x: x+inc, delta))
    import math
    zero_sum_count = min(int(4*round(count**0.5)), count)
    total_delta_2 = sum(delta[:zero_sum_count])
    inc2 = int(min(max(-total_delta_2/zero_sum_count, -10), 0))
    delta = list(map(lambda x: x+inc2, delta))
    for x, i in enumerate(delta):
        contestant[i].after_rating = contestant[i].before_rating+x
    return contestant
