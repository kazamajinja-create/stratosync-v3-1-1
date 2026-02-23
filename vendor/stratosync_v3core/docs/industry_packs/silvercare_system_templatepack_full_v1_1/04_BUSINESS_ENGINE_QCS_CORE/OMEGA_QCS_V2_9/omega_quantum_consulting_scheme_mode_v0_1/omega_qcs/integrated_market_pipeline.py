
from .engine_pipeline import run_business_competition_pipeline
from .external_market_context import build_market_context
from .market_sensitivity_model import compute_market_amplification
from .integrated_tendency_engine import integrate_tendency

def run_integrated_market_pipeline(financials=None, structure=None,
                                   market_inputs=None):
    base = run_business_competition_pipeline(financials=financials,
                                             structure=structure)
    market_inputs = market_inputs or {}
    market = build_market_context(
        market_inputs.get("MVI","中程度"),
        market_inputs.get("IGM","横ばい"),
        market_inputs.get("CPI","中圧"),
        market_inputs.get("RFI","中摩擦"),
    )
    amplification = compute_market_amplification(
        base["indices"].get("変動性指数","不明"),
        market.macro_volatility
    )
    integrated = integrate_tendency("内部傾向", amplification)

    base["market_context"] = market.__dict__
    base["integrated_tendency"] = integrated
    return base
