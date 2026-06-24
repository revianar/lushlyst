import pytest

from core.evaluator import evaluate_chemical_record


def test_evaluate_chemical_record_with_flammable_and_irritant_hazards():
    result = evaluate_chemical_record(
        {
            "cas_number": "67-64-1",
            "name": "Acetone",
            "ghs_classification": "Flammable liquid and vapor; Causes serious eye irritation",
            "toxicity_score": 4.5,
        }
    )

    assert result.health_score == 60
    assert result.safety_score == 70
    assert result.environmental_score == 0
    assert result.overall_risk_score == pytest.approx(43.33, rel=1e-3)
    assert result.risk_level == "moderate"


def test_evaluate_chemical_record_with_no_hazard_data_is_low_risk():
    result = evaluate_chemical_record(
        {
            "cas_number": "64-17-5",
            "name": "Ethanol",
            "ghs_classification": "No significant hazards",
            "toxicity_score": 0.0,
        }
    )

    assert result.health_score == 0
    assert result.safety_score == 0
    assert result.environmental_score == 0
    assert result.overall_risk_score == 0
    assert result.risk_level == "low"
