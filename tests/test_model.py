"""Tests for J_i decision model."""

import pytest

from heat_town.model import compute_contributions, compute_ji, normalize_weights


def test_compute_ji_balanced_weights():
    j = compute_ji(d=0.2, comfort=70.0, wbgt=28.0, w1=0.3, w2=0.4, w3=0.3)
    expected = 0.3 * 0.2 + 0.4 * (30.0 / 100.0) + 0.3 * (28.0 / 40.0)
    assert j == pytest.approx(expected)


def test_compute_ji_terms_bounded():
    j = compute_ji(d=2.0, comfort=-10.0, wbgt=100.0, w1=0.3, w2=0.4, w3=0.3)
    assert 0.0 <= j <= 1.0


def test_lower_ji_is_better_comfort():
    low_comfort = compute_ji(0.5, 40.0, 28.0, 0.3, 0.4, 0.3)
    high_comfort = compute_ji(0.5, 80.0, 28.0, 0.3, 0.4, 0.3)
    assert high_comfort < low_comfort


def test_normalize_weights():
    assert normalize_weights(1, 1, 1) == pytest.approx((1 / 3, 1 / 3, 1 / 3))


def test_normalize_weights_invalid():
    with pytest.raises(ValueError):
        normalize_weights(0, 0, 0)


def test_contributions_sum_to_total():
    c = compute_contributions(0.1, 65.0, 27.0, 0.3, 0.4, 0.3)
    assert c["distance"] + c["discomfort"] + c["heat"] == pytest.approx(c["total"])
