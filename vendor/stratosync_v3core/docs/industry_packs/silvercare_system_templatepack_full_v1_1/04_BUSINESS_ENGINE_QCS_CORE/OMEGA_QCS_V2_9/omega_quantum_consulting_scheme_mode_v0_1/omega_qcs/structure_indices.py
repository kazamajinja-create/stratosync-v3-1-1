
from typing import Dict

def extract_indices(snapshot: Dict) -> Dict[str,str]:
    return {
        "構造集中指数": snapshot.get("revenue_concentration"),
        "コスト硬直指数": snapshot.get("cost_structure"),
        "資金流動指数": snapshot.get("cashflow_pattern"),
        "変動性指数": snapshot.get("volatility_flag"),
    }
