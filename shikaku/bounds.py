"""Area-based upper bounds."""

def additional_bound(areas: list[int], used: frozenset[int], remaining: int) -> int:
    """Maximum number of cheapest unused representable areas fitting the budget."""
    count = 0
    for area in areas:
        if area in used:
            continue
        if area > remaining:
            break
        remaining -= area
        count += 1
    return count
