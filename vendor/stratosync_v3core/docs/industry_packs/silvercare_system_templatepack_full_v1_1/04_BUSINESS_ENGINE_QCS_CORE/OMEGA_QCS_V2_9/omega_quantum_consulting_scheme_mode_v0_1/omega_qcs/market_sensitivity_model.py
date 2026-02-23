
def compute_market_amplification(internal_index, market_index):
    if market_index in ["高", "非常に高い"]:
        return "増幅"
    elif market_index in ["低", "非常に低い"]:
        return "減衰"
    else:
        return "中立"
