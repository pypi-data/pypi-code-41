
def normal(mean, variance):
    return {
        'type__': 'distribution',
        'id': 'normal',
        'mean': mean,
        'variance': variance
    }

def poisson(rate):
    return {
        'type__': 'distribution',
        'id': 'poisson',
        'rate': rate,
    }

