def shorten_number(value):
    """
    Shortens a number to a more human-readable format.
    For example:
    1500 -> 1.5K
    2000000 -> 2M
    3500000000 -> 3.5B
    """
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return str(value)