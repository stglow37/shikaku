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


def _prime_sieve(limit: int) -> bytearray:
    """Return primality flags through limit in O(limit log log limit) time."""
    from math import isqrt

    prime = bytearray(b"\x01") * (limit + 1)
    prime[0:2] = b"\x00\x00"
    for divisor in range(2, isqrt(limit) + 1):
        if prime[divisor]:
            start = divisor * divisor
            count = (limit - start) // divisor + 1
            prime[start:limit + 1:divisor] = b"\x00" * count
    return prime


def area_upper_bound(n: int) -> int:
    """Compute the exact representable-area prefix bound U(n) via a sieve.

    For n >= 2, the only nonrepresentable integers through 2*n are primes
    exceeding n. The available prefix exceeds n*n before this range ends,
    so enumerating all n*n products is unnecessary. See docs/area_upper.md.
    This is a bound on k(n), not an assertion that those areas can be tiled.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    if n == 1:
        return 1
    prime = _prime_sieve(2 * n)
    count = n
    remaining = n * n - n * (n + 1) // 2
    for area in range(n + 1, 2 * n + 1):
        if prime[area]:
            continue
        if area > remaining:
            break
        remaining -= area
        count += 1
    return count
