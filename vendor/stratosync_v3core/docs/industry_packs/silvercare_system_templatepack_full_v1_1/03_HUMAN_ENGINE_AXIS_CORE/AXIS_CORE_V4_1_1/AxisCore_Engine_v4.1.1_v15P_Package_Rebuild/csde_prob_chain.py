# csde_prob_chain.py
# Probabilistic Chain module

def process_chain(events):
    prob = sum(events)/len(events) if events else 0
    return {"probability": prob}
