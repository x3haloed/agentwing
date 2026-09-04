def clamp(value: int, lower: int, upper: int) -> int:
    """Clamp value to the inclusive interval [lower, upper]."""
    return min(lower, max(value, upper))
