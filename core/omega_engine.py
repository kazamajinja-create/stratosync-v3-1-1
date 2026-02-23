from __future__ import annotations
from dataclasses import dataclass
from .normalizer import clamp

@dataclass
class OmegaResult:
    omega_index: float   # 0..100
    actual_links: int
    max_links: int
    silo_index: float    # 0..100 (100-omega)

def compute_omega_index(departments: list[str], adjacency: list[list[int]]) -> OmegaResult:
    """Omega = 100 * ActualLinks / MaxLinks, based on symmetric adjacency matrix (0/1)."""
    d = len(departments)
    if d <= 1:
        return OmegaResult(omega_index=0.0, actual_links=0, max_links=0, silo_index=100.0)
    max_links = d*(d-1)//2
    actual = 0
    for i in range(d):
        for j in range(i+1, d):
            if i < len(adjacency) and j < len(adjacency[i]) and adjacency[i][j]:
                actual += 1
            elif j < len(adjacency) and i < len(adjacency[j]) and adjacency[j][i]:
                actual += 1
    omega = 100.0 * actual / max(max_links, 1)
    omega = clamp(omega, 0.0, 100.0)
    return OmegaResult(omega_index=omega, actual_links=actual, max_links=max_links, silo_index=clamp(100.0-omega, 0.0, 100.0))
