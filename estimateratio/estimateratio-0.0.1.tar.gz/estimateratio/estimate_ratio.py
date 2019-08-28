from math import sqrt
from statistics import mean

def estimate_ratio(x, y, conf: float = 0.95):
    m_x = mean(x)
    m_y = mean(y)
    r = m_y / m_x
    s_r_2 = 1 / (len(x) - 1) * sum((y_i - r * x_i)^2 for x_i, y_i in zip(x, y))
    var_r = 1 / m_x^2 * s_r_2 / len(x)
    sd_r = sqrt(var_r)
    l = 2 / (3 * sqrt(1 - conf))
    return {
        'r': r,
        'variance': var_r,
        'sd': sd_r,
        'ci': (r - sd_r * l, r + sd_r * l)
    }
