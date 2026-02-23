# Default sensitivity matrix for 12 variables
# Values are 0..1 and can be overridden by industry dictionaries.
DEFAULT_SENSITIVITY_MATRIX = {
    "S": {"M": 0.6, "C": 0.5, "R": 0.7},
    "K": {"M": 0.5, "C": 0.6, "R": 0.5},
    "D": {"M": 0.7, "C": 0.6, "R": 0.6},
    "B": {"M": 0.6, "C": 0.7, "R": 0.5},
    "R": {"M": 0.6, "C": 0.5, "R": 0.8},
    "T": {"M": 0.7, "C": 0.5, "R": 0.6},
    "E": {"M": 0.5, "C": 0.8, "R": 0.5, "delta": 0.12},
    "H": {"M": 0.4, "C": 0.8, "R": 0.4, "delta": 0.12},
    "P": {"M": 0.5, "C": 0.6, "R": 0.6},
    "M": {"M": 0.6, "C": 0.5, "R": 0.5},
    "X": {"M": 0.5, "C": 0.7, "R": 0.4, "delta": 0.10},
    "G": {"M": 0.4, "C": 0.7, "R": 0.4, "delta": 0.10},
}
