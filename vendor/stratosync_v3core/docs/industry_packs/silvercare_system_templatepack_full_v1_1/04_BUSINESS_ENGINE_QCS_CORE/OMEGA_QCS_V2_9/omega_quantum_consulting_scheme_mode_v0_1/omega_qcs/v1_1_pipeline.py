
from .collision_model import compute_collision_intensity, compute_structural_resilience, compute_amplification_index
from .strategic_priority_generator import generate_strategic_priorities

def run_v1_1_engine(internal_scores, hssi, market_volatility, growth_momentum, sensitivity_map):
    ci = compute_collision_intensity(internal_scores, sensitivity_map)
    sr = compute_structural_resilience(hssi, market_volatility)
    ai = compute_amplification_index(hssi, growth_momentum)
    priority = generate_strategic_priorities(ci)

    return {
        "collision_intensity": ci,
        "structural_resilience": sr,
        "amplification_index": ai,
        "strategic_priority": priority
    }
