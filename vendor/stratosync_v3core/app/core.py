from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from typing import Dict, List, Tuple

@dataclass
class EvalParams:
    wp: float = 0.4
    wc: float = 0.3
    we: float = 0.3
    alpha: float = 0.2
    Pf: float = 0.2
    Cf: float = 0.2
    Ef: float = 0.2
    delta_go: float = 0.25
    S_go: float = 0.65
    delta_cond: float = 0.45

def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else float(x)

def evaluate(P: float, C: float, E: float, eta: float, params: EvalParams) -> Tuple[Dict, List[str]]:
    P = _clamp01(P); C = _clamp01(C); E = _clamp01(E); eta = _clamp01(eta)

    reasons: List[str] = []

    # Noise filter
    Pp = P * (1.0 - eta)
    Cp = C * (1.0 - eta)
    Ep = E * (1.0 - eta)

    # Weighted sync score
    S = params.wp * Pp + params.wc * Cp + params.we * Ep

    # Misalignment distance
    delta = sqrt((Pp - Ep)**2 + (Pp - Cp)**2 + (Cp - Ep)**2)

    # Psi adjusted execution
    psi = Ep * (1.0 + params.alpha * Pp)

    # Hard freeze (safety)
    if P < params.Pf:
        reasons.append(f"Hard freeze: political_score {P:.3f} < {params.Pf:.3f}")
    if C < params.Cf:
        reasons.append(f"Hard freeze: capital_score {C:.3f} < {params.Cf:.3f}")
    if E < params.Ef:
        reasons.append(f"Hard freeze: execution_score {E:.3f} < {params.Ef:.3f}")

    if reasons:
        state = "FREEZE"
    else:
        # GO
        if (delta <= params.delta_go) and (S >= params.S_go):
            state = "GO"
            reasons.append(f"GO band: delta {delta:.3f} <= {params.delta_go:.3f} and S {S:.3f} >= {params.S_go:.3f}")
        # Conditional
        elif delta <= params.delta_cond:
            state = "CONDITIONAL"
            reasons.append(f"Conditional band: delta {delta:.3f} <= {params.delta_cond:.3f}")
        else:
            state = "FREEZE"
            reasons.append(f"Freeze: delta {delta:.3f} > {params.delta_cond:.3f}")

    outputs = {
        "political_filtered": Pp,
        "capital_filtered": Cp,
        "execution_filtered": Ep,
        "synchronization_score": S,
        "delta_index": delta,
        "psi_adjusted_execution": psi,
        "system_state": state,
        "reasons": reasons,
    }
    return outputs, reasons
