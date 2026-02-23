
from dataclasses import dataclass

@dataclass
class MarketContext:
    macro_volatility: str
    industry_growth: str
    competitive_pressure: str
    regulatory_friction: str

def build_market_context(mvi, igm, cpi, rfi):
    return MarketContext(mvi, igm, cpi, rfi)
