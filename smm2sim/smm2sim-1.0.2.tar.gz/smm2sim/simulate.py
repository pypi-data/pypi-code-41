from .players import Player, Players
from scipy import stats
import pandas as pd
import numpy as np

#simulates games in a gamelog using standard method
def simulateGamelog(gamelog, rankings, st_dev):
    merged = pd.merge(gamelog, rankings.rename({'Player':'Home'}, axis=1), on='Home').rename({'PWR':'Home PWR'}, axis=1)
    merged = pd.merge(merged, rankings.rename({'Player':'Away'}, axis=1), on='Away').rename({'PWR':'Away PWR'}, axis=1)
    dist = stats.norm(merged['Home PWR'].values - merged['Away PWR'].values, st_dev)
    test_vals = 1 - dist.cdf(0)
    random_vals = np.random.random((3, merged.shape[0]))
    home_win = np.sum(np.less(random_vals, test_vals).astype(int), axis=0)
    merged['Winner'] = np.where(np.greater(home_win, 1), merged['Home'], merged['Away'])
    merged['Loser'] = np.where(np.greater(home_win, 1), merged['Away'], merged['Home'])
    merged['W Pts'] = np.where(np.isin(home_win, [1, 2]), 3, 4)
    merged['L Pts'] = 4 - merged['W Pts'].values
    return merged[['Winner','Loser','W Pts','L Pts']]

#simulates a "bracket"-style group of games between seeded teams
def simulateBracket(players, st_dev, n_winners=1):
    def getWinners(matchups, results=None, round_n=None, seriescounter=None):
        def roundCount(matchups):
            return 1 + (0 if not isinstance(matchups[0], list) else roundCount(matchups[0]))
        original_call = False
        if round_n is None:
            original_call = True
            results = []
            round_n = roundCount(matchups)
            seriescounter = {x:0 for x in range(round_n + 1)}
        if isinstance(matchups[0], list):
            round_n -= 1
            winner_a = getWinners(matchups[0], results, round_n, seriescounter)
            winner_b = getWinners(matchups[1], results, round_n, seriescounter)
            winner = getWinners([winner_a, winner_b], results, round_n + 1, seriescounter)
            if original_call:
                final_results = {}
                cumulative_series_count = {-1:0}
                for i, x in seriescounter.items():
                    cumulative_series_count[i] = cumulative_series_count[i - 1] + x
                for i, x in enumerate(results):
                    result = {'Winner':x['Winner'],'Loser':x['Loser'],'Games':x['Games']}
                    final_results[cumulative_series_count[x['Round'] - 1] + x['Series']] = result
                return final_results
            else:
                return winner
        else:
            result = simulateMatch(matchups[0], matchups[1], st_dev=st_dev)
            seriescounter[round_n] = seriescounter[round_n] + 1
            results.append({'Winner':result['Winner'].name,'Loser':result['Loser'].name,
                            'Games':result['Games'],'Round':round_n,'Series':seriescounter[round_n]})
            return result['Winner']
    n_players = players.len()
    remaining = players
    results = {}
    remaining.index(seed=True)
    remaining_seeds = [x[0] for i, x in remaining.items()]
    seeds = remaining_seeds
    while True:
        seeds = [[seeds[i], seeds[-i-1]] for i in range(int(len(seeds) / 2))]
        if len(seeds) == 2:
            break
    return getWinners(seeds)

def simulateMatch(player_a, player_b, st_dev):
    n_games = 3
    target_wins = 2
    pwr_difference = [player_a.pwr - player_b.pwr] * n_games
    win_probability = 1 - stats.norm(pwr_difference, st_dev).cdf(0)
    is_winner = (np.random.random(n_games) < win_probability).astype(int)
    a_wins = 0
    b_wins = 0
    for i in range(n_games):
        a_wins += is_winner[i]
        b_wins += 1 - is_winner[i]
        if a_wins == target_wins:
            return {'Winner':player_a,'Loser':player_b,'Games':i + 1}
        elif b_wins == target_wins:
            return {'Winner':player_b,'Loser':player_a,'Games':i + 1}