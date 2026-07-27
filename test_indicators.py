import pytest

from aed.indicators import Indicator


def test_verified_indicator_requires_source():
    indicator = Indicator(
        code="RS",
        name="Reliability of service",
        definition="Continuity and predictability of electricity service.",
        unit="hours/day",
        direction="higher_is_better",
        evidence_status="observed",
    )

    with pytest.raises(ValueError, match="source is required"):
        indicator.validate()


def test_assumption_can_be_recorded_without_external_source():
    indicator = Indicator(
        code="PU",
        name="Productive-use assumption",
        definition="Scenario assumption for productive electricity demand.",
        unit="kWh/day",
        direction="target",
        evidence_status="assumed",
    )

    indicator.validate()
