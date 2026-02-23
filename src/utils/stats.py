from __future__ import annotations
import math
import numpy as np
from scipy import stats

def welch_ttest(a: np.ndarray, b: np.ndarray):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    t_stat, p_val = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
    return float(t_stat), float(p_val)

def diff_in_proportions(p1: float, n1: int, p2: float, n2: int, alpha: float = 0.05):
    # normal approx CI for difference in proportions
    se = math.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    z = stats.norm.ppf(1 - alpha/2)
    diff = p2 - p1
    lo, hi = diff - z*se, diff + z*se
    return diff, (float(lo), float(hi))

def bootstrap_ci(values: np.ndarray, stat_fn=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 7):
    rng = np.random.default_rng(seed)
    values = np.asarray(values)
    boots = []
    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        boots.append(stat_fn(sample))
    boots = np.sort(np.asarray(boots))
    lo = np.quantile(boots, alpha/2)
    hi = np.quantile(boots, 1-alpha/2)
    return float(lo), float(hi)
