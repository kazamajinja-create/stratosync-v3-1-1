from __future__ import annotations

import math
from typing import Dict, Any

TAXICAB_1729 = {
    "n": 1729,
    "representations": [
        {"a": 1, "b": 12, "sum": 1**3 + 12**3},
        {"a": 9, "b": 10, "sum": 9**3 + 10**3},
    ],
    "note": "Smallest number expressible as sum of two cubes in two distinct ways."
}

def partition_estimate(n: int) -> Dict[str, Any]:
    """Hardy–Ramanujan asymptotic estimate for p(n) (integer partitions).

    p(n) ~ 1/(4n*sqrt(3)) * exp(pi*sqrt(2n/3))

    Returns both estimate and log-estimate for stable scaling.
    Deterministic; not intended for exact p(n).
    """
    n = int(max(0, n))
    if n <= 0:
        return {"n": n, "p_est": 1.0, "log_p_est": 0.0}
    root = math.sqrt(2.0 * n / 3.0)
    exponent = math.pi * root
    # To avoid overflow for large n, use logs
    log_p = exponent - math.log(4.0 * n * math.sqrt(3.0))
    p_est = float(math.exp(min(log_p, 700)))  # cap for float safety
    return {
        "n": n,
        "formula": "p(n) ~ exp(pi*sqrt(2n/3)) / (4n*sqrt(3))",
        "p_est": p_est,
        "log_p_est": float(log_p),
    }

def ramanujan_pi_approx(terms: int = 1) -> Dict[str, Any]:
    """Ramanujan's rapidly convergent series for 1/pi.

    1/pi = (2*sqrt(2)/9801) * sum_{k>=0} (4k)! (1103 + 26390k) / ((k!)^4 396^{4k})

    We compute a small number of terms for demo purposes.
    """
    terms = int(max(1, min(5, terms)))  # keep cheap
    factor = 2.0 * math.sqrt(2.0) / 9801.0
    s = 0.0
    for k in range(terms):
        num = math.factorial(4*k) * (1103.0 + 26390.0*k)
        den = (math.factorial(k)**4) * (396.0**(4*k))
        s += num / den
    inv_pi = factor * s
    pi_est = 1.0 / inv_pi
    return {
        "terms": terms,
        "pi_est": float(pi_est),
        "note": "Demo only; a few terms yield high precision, but we keep it bounded for runtime."
    }
