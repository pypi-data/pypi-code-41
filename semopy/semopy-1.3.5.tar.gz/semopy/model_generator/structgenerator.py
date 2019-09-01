'''This module contains methods that generate structural and measurement parts
of a SEM model.'''


from numpy.random import uniform, randint
from random import choice, shuffle
from itertools import combinations
from .utils import ThreadsManager

def generate_measurement_part(num_latents, num_indicators=(2, 3),
                              percentage_inds=0.0, name_latent='eta',
                              name_indicator='y'):
    '''Generates latent variables and their respective indicators.
    
    Keyword arguments:
    
        num_latents      -- A number of latent variables.
    
        num_indicators   -- A number of indicator variables per latent (a tuple).
    
        percentage_inds  -- A percentage of manifest variables to be joined
                            together.
    
        name_latent      -- A name prefix for latent variables ("eta" by default).
    
        name_indicator   -- A name prefix for indicator variable ("y" by default).
    
    Returns:
    
        A measurement part.
    '''
    def select_manif_set(m_part, n):
        keys = list(m_part.keys())
        shuffle(keys)
        inds = set()
        for key in keys:
            t = list(m_part[key].difference(inds))
            if t:
                inds.add(choice(t))
                if len(inds) >= n:
                    break
        return list(inds)
    m_part = {'{}{}'.format(name_latent, i + 1): set()
              for i in range(num_latents)}
    inds_count = 0
    num_indsA, num_indsB = num_indicators
    for lv in m_part:
        inds = m_part[lv]
        num_inds = choice(range(num_indsA, num_indsB + 1))
        for i in range(num_inds):
            name = '{}{}'.format(name_indicator, inds_count + i + 1)
            inds.add(name)
        inds_count += num_inds
    m = int(percentage_inds * inds_count)
    s = select_manif_set(m_part, 2)
    n = len(s)
    while n > 1 and m > 0:
        base = s[0]
        s = s[1:]
        for lv in m_part:
            for ind in s:
                if ind in m_part[lv]:
                    m_part[lv].remove(ind)
                    m_part[lv].add(base)
        m -= n - 1
        s = select_manif_set(m_part, 2)
        n = len(s)
    return m_part


#def generate_structural_part(m_part: dict, num_observed: int, num_cycles=0,
#                             num_lvs_unconnected=0, name_observed='x',
#                             names_observed=list()):
#    '''
#Keyword arguments:
#    m_part              -- A measurement part to incorporate into a structural
#                           part (including latents).
#    num_observed:       -- A number of observed variables.
#    num_cycles          -- A maximal number of cycles.
#    num_lvs_unconnected -- A number of unconnected to each other latent
#                           variables.
#    name_observed       -- A name prefix for observable variables.
#    names_observed      -- A predefinex list of names for the first n observed
#                           variables.
#Returns:
#    A structural part and an auxillary by-product ThreadsManager.
#    '''
#    tm = ThreadsManager()
#    latents = list(m_part.keys())
#    variables = latents.copy()
#    boundary = len(latents) - num_lvs_unconnected
#    if boundary <= 1:
#        for v in latents:
#            tm.add_node(v)
#    else:
#        for v in islice(latents, boundary, len(latents)):
#            tm.add_node(v)
#        latents_sliced = latents[:boundary]
#        shuffle(latents_sliced)
#        for i, a in enumerate(islice(latents_sliced, boundary - 1)):
#            b = latents_sliced[randint(i + 1, boundary)]
#            if uniform() > 0.5:
#                a, b = b, a
#            tm.connect_nodes(a, b)
#    it = iter(range(num_observed))
#    if boundary == 0:
#        first = next(it)
#        if first < len(names_observed):
#            node = names_observed[i]
#        else:
#            node = '{}{}'.format(name_observed, 1)
#        variables.append(node)
#
#    for i in it:
#        if i < len(names_observed):
#            a = names_observed[i]
#        else:
#            a = '{}{}'.format(name_observed, i + 1 - len(names_observed))
#        b = choice(variables)
#        variables.append(a)
#        if uniform() > 0.5:
#            a, b = b, a
#        tm.connect_nodes(a, b)
#    if num_cycles > 0:
#        cyclable_vars = [v for v in variables if tm.get_node_order(v) > 2]
#        if cyclable_vars:
#            for i in range(num_cycles):
#                a = choice(cyclable_vars)
#                threads = [thread for thread in tm.find_threads(a)
#                           if thread.index(a) > 2]
#                thread = choice(threads)
#                order = thread.index(a)
#                # We want neither exogenous variables to be sacrificed, nor
#                # those variables, that go just right before.
#                b = thread[randint(1, order - 1)]
#                tm.connect_nodes(a, b)
#    return tm.translate_to_dict(), tm


def generate_structural_part(m_part: dict, num_observed: int, num_cycles=0,
                             name_observed='x', forbid_endogeneous=False,
                             fe_obs_per_lat=None, fe_percentage_obs=0.0,
                             names_observed=list()):
    '''Generates a structural part.

    Keyword arguments:

        m_part              -- A measurement part to incorporate into a structural
                               part (including latents).

        num_observed:       -- A number of observed variables.
        
        num_cycles          -- A maximal number of cycles.
        
        name_observed       -- A name prefix for observable variables.
        
        forbid_endogeneous  -- Forbids endogeneous variables for observed
                               variables.
        
        fe_obs_per_lat      -- If forbid_endogeneous is true, then this arg
                               can specify (if not None) a range of observed
                               variables per latent (similarily to manifest
                               variables per latent variable).
        
        fe_percentage_obs   -- If forbid_endogeneous is True and 
                               fe_exos_per_lat is a tuple, then it specifies
                               percentage of observed variables to be joined
                               together similariy to manifest variables.
                               
                               
        names_observed      -- A predefined list of names for the first n observed
                               variables.

    Returns:

        A structural part and an auxillary by-product ThreadsManager.
    '''
    tm = ThreadsManager()
    observed = ['{}{}'.format(name_observed, i + 1)
                if i >= len(names_observed) else names_observed[i]
                for i in range(num_observed)]
    nodes_stack = list(m_part.keys())
    if not forbid_endogeneous:
        nodes_stack.extend(observed)
    shuffle(nodes_stack)
    nodes_added = [nodes_stack.pop()]
    while nodes_stack:
        a = choice(nodes_added)
        b = nodes_stack.pop()
        nodes_added.append(b)
        if uniform() > 0.5:
            a, b = b, a
        tm.connect_nodes(a, b)
    if forbid_endogeneous:
        if not fe_obs_per_lat:
            for obs in observed:
                lat = choice(nodes_stack)
                tm.connnect_nodes(obs, lat)
        else:
            d_lat = dict()
            c = 1
            for lat in m_part:
                n = randint(*fe_obs_per_lat)
                a, b = c, c + n
                d_lat[lat] = set(range(a, b))
                c = b
            for _ in range(0, int(c * fe_percentage_obs)):
                lt = list()
                for a, b in combinations(m_part.keys(), 2):
                    a_diff = d_lat[a].difference(d_lat[b])
                    b_diff = d_lat[b].difference(d_lat[a])
                    if a_diff and b_diff:
                        lt.append((a, b, a_diff, b_diff))
                if not lt:
                    break
                a, b, a_obs, b_obs = choice(lt)
                a_obs, b_obs = choice(list(a_obs)), choice(list(b_obs))
                d_lat[b].remove(b_obs)
                d_lat[b].add(a_obs)
            names = dict()
            for lat, obses in d_lat.items():
                for obs in obses:
                    if obs not in names:
                        names[obs] = '{}{}'.format(name_observed,
                                                   len(names) + 1)
                    tm.connect_nodes(names[obs], lat)
    if num_cycles > 0:
        cyclable_vars = [v for v in nodes_added if tm.get_node_order(v) > 2]
        if cyclable_vars:
            for i in range(num_cycles):
                a = choice(cyclable_vars)
                threads = [thread for thread in tm.find_threads(a)
                           if thread.index(a) > 2]
                thread = choice(threads)
                order = thread.index(a)
                # We want neither exogenous variables to be sacrificed, nor
                # those variables, that go just right before.
                b = thread[randint(1, order - 1)]
                tm.connect_nodes(a, b)
    return tm.translate_to_dict(), tm


def create_model_description(mpart: dict, spart: dict):
    '''Creates a model description in a text form using respective measurement
    part and structural part.
    
Keyword arguments:
    
    mpart -- A measurement part.
    
    spart -- A structural part.
    
Returns:
    
    A string containing model's description.
    '''
    def translate(d: dict, op: str):
        ret = str()
        for v, variables in d.items():
            s = '{} {} '.format(v, op)
            it = iter(sorted(variables))
            s += next(it)
            for var in it:
                s += ' + {}'.format(var)
            ret += s + '\n'
        return ret
    return translate(mpart, '=~') + translate(spart, '~')
