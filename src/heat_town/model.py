"""Decision model J_i computation."""

from __future__ import annotations


def compute_ji(
    d: float,
    comfort: float,
    wbgt: float,
    w1: float,
    w2: float,
    w3: float,
) -> float:
    """Compute J_i = w1*d + w2*(100-C) + w3*WBGT."""
    return w1 * d + w2 * (100.0 - comfort) + w3 * wbgt


def normalize_weights(w1: float, w2: float, w3: float) -> tuple[float, float, float]:
    """Normalize weights to sum to 1."""
    total = w1 + w2 + w3
    if total <= 0:
        raise ValueError("weights must sum to a positive value")
    return w1 / total, w2 / total, w3 / total


def compute_contributions(
    d: float,
    comfort: float,
    wbgt: float,
    w1: float,
    w2: float,
    w3: float,
) -> dict[str, float]:
    """Return per-term contributions for explainability."""
    nw1, nw2, nw3 = normalize_weights(w1, w2, w3)
    return {
        "distance": nw1 * d,
        "discomfort": nw2 * (100.0 - comfort),
        "heat": nw3 * wbgt,
        "total": compute_ji(d, comfort, wbgt, nw1, nw2, nw3),
    }
