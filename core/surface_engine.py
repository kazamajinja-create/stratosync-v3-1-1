from __future__ import annotations
from dataclasses import dataclass
from .normalizer import clamp, avg

@dataclass
class SurfaceAxes:
    CT: float  # Customer Touch 0..100
    AL: float  # API/Tech Link 0..100
    PN: float  # Partner Network 0..100
    BE: float  # Brand Exposure 0..100
    DC: float  # Data Contact 0..100

def compute_surface_index(ax: SurfaceAxes) -> float:
    """SI = 0.30*CT + 0.20*AL + 0.20*PN + 0.15*BE + 0.15*DC"""
    si = 0.30*ax.CT + 0.20*ax.AL + 0.20*ax.PN + 0.15*ax.BE + 0.15*ax.DC
    return clamp(si, 0.0, 100.0)

def compute_internal_resource_index(HC: float, CB: float, PM: float, MT: float) -> float:
    """IRI = 0.35*HC + 0.30*CB + 0.20*PM + 0.15*(100-MT)"""
    iri = 0.35*HC + 0.30*CB + 0.20*PM + 0.15*(100.0 - MT)
    return clamp(iri, 0.0, 100.0)

def compute_surface_efficiency(SI: float, IRI: float) -> float:
    """RawSE = SI/max(IRI,10); SE = clamp(20*RawSE,0,100)"""
    raw = SI / max(IRI, 10.0)
    se = 20.0 * raw
    return clamp(se, 0.0, 100.0)
