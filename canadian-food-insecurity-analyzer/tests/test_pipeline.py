import pandas as pd
import pytest

from src.pipeline import build_change_tables, build_panel, validate_visits


def test_real_sources_have_expected_coverage():
    panel, insecurity, profile = build_panel()
    visits = panel.dropna(subset=["total_visits"])
    assert set(visits.year.astype(int)) == {2019, 2024, 2025}
    assert visits.groupby("year").province_code.nunique().eq(10).all()
    assert insecurity.groupby("year").province_code.nunique().eq(10).all()
    assert set(profile.year) == {2019, 2024, 2025}


def test_published_national_totals_reconcile():
    panel, _, _ = build_panel()
    visits = panel.dropna(subset=["total_visits"])
    assert int(visits[visits.year == 2019].total_visits.sum()) == 1_080_531
    assert int(visits[visits.year == 2024].total_visits.sum()) == 2_055_652
    assert int(visits[visits.year == 2025].total_visits.sum()) == 2_160_869


def test_manitoba_long_change_is_suppressed():
    panel, _, _ = build_panel()
    mb = panel[(panel.province_code == "MB") & (panel.year == 2025)].iloc[0]
    assert pd.isna(mb.change_since_2019_pct)


def test_change_tables_identify_distinct_leaders():
    panel, insecurity, _ = build_panel()
    visits, food_insecurity = build_change_tables(panel, insecurity)
    comparable = visits[visits["comparable_to_2019"]]
    assert comparable.loc[comparable["absolute_change"].idxmax(), "province_code"] == "ON"
    assert comparable.loc[comparable["percent_change"].idxmax(), "province_code"] == "AB"
    assert food_insecurity.iloc[0]["province_code"] == "SK"


def test_validation_rejects_duplicates():
    panel, _, _ = build_panel()
    cols = ["year", "province_code", "province", "total_visits", "child_visits",
            "reporting_food_banks", "comparable_to_2019", "source_page"]
    sample = panel.dropna(subset=["total_visits"])[cols].head(2)
    with pytest.raises(ValueError, match="Duplicate"):
        validate_visits(pd.concat([sample, sample.iloc[[0]]]))
