import pytest

from Relative_Valuation.relative_valuation_calculator import allocate_dynamic_weights


def test_allocate_dynamic_weights_respects_custom_schema():
    available = {
        'net_asking_rent': True,
        'parking_ratio': True,
        'tmi': True,  # Provided but intentionally weighted to zero
    }
    base_weights = {
        'net_asking_rent': 0.7,
        'parking_ratio': 0.3,
        'tmi': 0.0,
    }

    weights = allocate_dynamic_weights(available, base_weights)

    assert weights['net_asking_rent'] == pytest.approx(0.7, rel=1e-4)
    assert weights['parking_ratio'] == pytest.approx(0.3, rel=1e-4)
    assert weights['tmi'] == pytest.approx(0.0, abs=1e-6)


def test_allocate_dynamic_weights_handles_percentage_inputs():
    available = {
        'net_asking_rent': True,
        'parking_ratio': True,
    }
    base_weights = {
        'net_asking_rent': 60,  # Percent style
        'parking_ratio': 40,
    }

    weights = allocate_dynamic_weights(available, base_weights)

    assert weights['net_asking_rent'] == pytest.approx(0.6, rel=1e-4)
    assert weights['parking_ratio'] == pytest.approx(0.4, rel=1e-4)


def test_allocate_dynamic_weights_uses_defaults_when_missing():
    available = {
        'net_asking_rent': True,
        'tmi': True,
        'parking_ratio': False,
    }

    weights = allocate_dynamic_weights(available, {})

    assert weights['net_asking_rent'] == pytest.approx(0.5385, rel=1e-4)
    assert weights['tmi'] == pytest.approx(0.4615, rel=1e-4)
