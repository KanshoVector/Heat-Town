"""Decision model J_i computation."""

from __future__ import annotations

WBGT_SCALE = 40.0


def normalize_ji_terms(
    d: float,
    comfort: float,
    wbgt: float,
) -> tuple[float, float, float]:
    """Return dimensionless terms in [0, 1]: d, (100-C)/100, WBGT/40."""
    d_n = max(0.0, min(float(d), 1.0))
    discomfort_n = max(0.0, min((100.0 - float(comfort)) / 100.0, 1.0))
    wbgt_n = max(0.0, min(float(wbgt) / WBGT_SCALE, 1.0))
    return d_n, discomfort_n, wbgt_n


def compute_ji(
    d: float,
    comfort: float,
    wbgt: float,
    w1: float,
    w2: float,
    w3: float,
) -> float:
    """Compute J_i = w1*d + w2*(100-C)/100 + w3*(WBGT/40), all terms in [0, 1]."""
    d_n, discomfort_n, wbgt_n = normalize_ji_terms(d, comfort, wbgt)
    return w1 * d_n + w2 * discomfort_n + w3 * wbgt_n


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
    d_n, discomfort_n, wbgt_n = normalize_ji_terms(d, comfort, wbgt)
    return {
        "distance": nw1 * d_n,
        "discomfort": nw2 * discomfort_n,
        "heat": nw3 * wbgt_n,
        "total": compute_ji(d, comfort, wbgt, nw1, nw2, nw3),
    }
