import math


def calculate_pages(total: int, size: int) -> int:
    """Calculate total number of pages. Always returns at least 1."""
    if size <= 0:
        return 1
    return max(1, math.ceil(total / size))
