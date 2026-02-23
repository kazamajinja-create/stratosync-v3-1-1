# Quantum Seed Mapper

def map_term_to_seed(term):
    return hash(term) % 1024