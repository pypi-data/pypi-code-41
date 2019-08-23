from scipy import stats
import numpy as np

def t_test(v, weights=None, opts={'paired': False, 'equal_variance': False}, one_sided=False): # unpaired, unequal variance
    base = np.nansum(~np.isnan(v)*1, axis=1)
    if weights is not None:
        score, dof = weighted_t_test_(v, weights)
    else:
        score, dof = standard_t_test_(v, weights, opts)
    p_values = stats.t.sf(np.abs(score), dof)
    p_values *= (1 if one_sided else 2)
    return p_values, score

def weighted_t_test_(v, weights):
    base = np.nansum(~np.isnan(v)*1, axis=1)
    weighted_count = np.nansum(weights, axis=1)
    mean = np.nansum(v * weights, axis=1) / np.nansum(weights, axis=1)
    t_nom = mean[:, np.newaxis] - mean
    var = np.sqrt(np.nansum(((v.T - mean)**2) * weights.T, axis=0) / np.nansum(weights, axis=1))**2
    t_denom = weighted_count * var + weighted_count[:, np.newaxis] * var[:, np.newaxis]
    inv_base = 1/weighted_count + 1/weighted_count[:, np.newaxis]
    dof = base + base[:, np.newaxis] - 2
    score = t_nom / np.sqrt((t_denom * inv_base) / dof)
    return score, dof

def standard_t_test_(v, weights, opts):
    if opts['paired']:
        return paired_t_test_(v, weights)
    base = np.nansum(~np.isnan(v)*1, axis=1)
    mean = np.nanmean(v, axis=1)
    t_nom = mean[:, np.newaxis] - mean
    s = np.nanvar(v, axis=1, ddof=1)
    if opts['equal_variance']:
        sp = ((base - 1) * s + (base[:, np.newaxis] - 1) * s[:, np.newaxis]) / (base + base[:, np.newaxis] - 2)
        score = t_nom / (np.sqrt(sp) * np.sqrt(1 / base + 1 / base[:, np.newaxis]))
        dof = base + base[:, np.newaxis] - 2
    else:
        s_n = s / base
        score = t_nom / np.sqrt(s_n + s_n[:, np.newaxis])
        dof_denom = (s_n**2 / (base - 1)) + (s_n[:, np.newaxis]**2 / (base[:, np.newaxis] - 1))
        dof = (s_n + s_n[:, np.newaxis])**2 / dof_denom
    return score, dof

def paired_t_test_(v, weights):
    dof = v.T.shape[0] - 1
    x_d = np.nanmean(v[:, np.newaxis] - v, axis=2)
    s_d = np.nanstd(v - v[:, np.newaxis], axis=2, ddof=1)
    t = x_d / (s_d / np.sqrt(v.shape[0]))
    score = x_d / (s_d / np.sqrt(v.T.shape[0]))
    score[np.isnan(score)] = 0
    return score, dof

def percentage_t_test(v, weights=None, opts={'distribution': 't'}, one_sided=False):
    base = ~np.isnan(v)*1
    mean = np.nanmean(v, axis=1)
    nansum = np.nansum(v, axis=1)
    pooled_percentage = (nansum + nansum[:, np.newaxis]) / (base + base[:, np.newaxis]).sum(axis=2)
    inv = 1 / base.sum(axis=1)
    if weights is not None:
        mean = np.nansum(v * weights, axis=1) / np.nansum(weights, axis=1)
        weighted_sum = np.nansum(weights, axis=1)
        pooled_percentage = (mean * weighted_sum + mean[:, np.newaxis] * weighted_sum[:, np.newaxis]) / (weighted_sum + weighted_sum[:, np.newaxis])
        inv = 1 / weighted_sum
    inv_base = inv + inv[:, np.newaxis]
    pooled_std_error = np.sqrt(pooled_percentage * (1.0 - pooled_percentage) * inv_base)
    score = (mean[:, np.newaxis] - mean) / pooled_std_error
    if opts['distribution'] == 'z':
        p_values = 1 - stats.norm.cdf(np.abs(score))
    elif opts['distribution'] == 't':
        dof = (base + base[:, np.newaxis]).sum(axis=2) - 2
        p_values = stats.t.sf(np.abs(score), dof)
    p_values *= (1 if one_sided else 2)
    return p_values, score

def one_sample_z_test(v, population_proportion, tails=2):
    return one_sample_z_test_simple(v.sum(axis=1), v.shape[1], population_proportion, tails)

def one_sample_z_test_simple(count, sample_size, population_proportion, tails=2):
    ratios = count / sample_size
    standard_error = (population_proportion * (1.0 - population_proportion) / sample_size) ** 0.5
    score = (ratios - population_proportion) / standard_error
    p_values = (1.0 - stats.norm.cdf(np.abs(score))) * tails
    return p_values, score
