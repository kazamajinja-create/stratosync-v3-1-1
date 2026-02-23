from dataclasses import dataclass

@dataclass
class Thresholds:
    collision_lvl1: float = 80.0
    collision_lvl2: float = 50.0
    resilience_high: float = 1.5
    resilience_mid: float = 1.0

@dataclass
class Scales:
    # internal numeric layer ranges (non-public)
    internal_min: float = 0.0
    internal_max: float = 100.0
    market_min: float = 0.0
    market_max: float = 4.0

DEFAULT_THRESHOLDS = Thresholds()
DEFAULT_SCALES = Scales()
