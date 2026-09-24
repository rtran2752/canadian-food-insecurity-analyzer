"""Validate and combine the project's real, public Canadian datasets."""
from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR


def validate_visits(df: pd.DataFrame) -> None:
    required = {
        "year", "province_code", "province", "total_visits", "child_visits",
        "reporting_food_banks", "comparable_to_2019", "source_page",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Visits file missing columns: {sorted(missing)}")
    if df.duplicated(["year", "province_code"]).any():
        raise ValueError("Duplicate year/province visit record")
    if (df[["total_visits", "child_visits", "reporting_food_banks"]] < 0).any().any():
        raise ValueError("Visit counts cannot be negative")
    if (df["child_visits"] > df["total_visits"]).any():
        raise ValueError("Child visits cannot exceed total visits")


def build_panel(raw_dir=RAW_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    visits = pd.read_csv(raw_dir / "food_bank_visits.csv")
    insecurity = pd.read_csv(raw_dir / "food_insecurity_people_pct.csv")
    profile = pd.read_csv(raw_dir / "national_client_profile.csv")
    validate_visits(visits)

    visits["child_share_pct"] = visits["child_visits"] / visits["total_visits"] * 100
    visits["visits_per_reporting_food_bank"] = (
        visits["total_visits"] / visits["reporting_food_banks"]
    )
    visits["yoy_visits_pct"] = visits.groupby("province_code")["total_visits"].pct_change() * 100

    base = visits[visits.year == 2019][["province_code", "total_visits"]].rename(
        columns={"total_visits": "visits_2019"}
    )
    visits = visits.merge(base, on="province_code", how="left")
    visits["change_since_2019_pct"] = (
        (visits["total_visits"] / visits["visits_2019"] - 1) * 100
    ).where(visits["comparable_to_2019"])

    panel = visits.merge(
        insecurity, on=["year", "province_code", "province"], how="outer",
        validate="one_to_one",
    ).sort_values(["year", "province_code"])
    return panel, insecurity, profile


def build_change_tables(
    panel: pd.DataFrame, insecurity: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create explicit, ranked comparisons for the headline questions."""
    visit_rows = panel[panel["year"].isin([2019, 2025])].dropna(subset=["total_visits"])
    visit_change = visit_rows.pivot(
        index=["province_code", "province"], columns="year", values="total_visits"
    ).reset_index().rename(columns={2019: "visits_2019", 2025: "visits_2025"})
    comparable = visit_rows[visit_rows["year"] == 2025][
        ["province_code", "comparable_to_2019"]
    ].drop_duplicates()
    visit_change = visit_change.merge(comparable, on="province_code", how="left")
    visit_change["absolute_change"] = visit_change["visits_2025"] - visit_change["visits_2019"]
    visit_change["percent_change"] = (
        visit_change["absolute_change"] / visit_change["visits_2019"] * 100
    ).where(visit_change["comparable_to_2019"])
    visit_change["absolute_rank"] = (
        visit_change["absolute_change"].where(visit_change["comparable_to_2019"])
        .rank(method="min", ascending=False)
    )
    visit_change["percent_rank"] = visit_change["percent_change"].rank(
        method="min", ascending=False
    )
    visit_change = visit_change.sort_values("absolute_change", ascending=False)

    insecurity_rows = insecurity[insecurity["year"].isin([2019, 2024])]
    insecurity_change = insecurity_rows.pivot(
        index=["province_code", "province"], columns="year", values="food_insecurity_pct"
    ).reset_index().rename(
        columns={2019: "food_insecurity_2019_pct", 2024: "food_insecurity_2024_pct"}
    )
    insecurity_change["percentage_point_change"] = (
        insecurity_change["food_insecurity_2024_pct"]
        - insecurity_change["food_insecurity_2019_pct"]
    )
    insecurity_change["change_rank"] = insecurity_change[
        "percentage_point_change"
    ].rank(method="min", ascending=False)
    insecurity_change = insecurity_change.sort_values(
        "percentage_point_change", ascending=False
    )
    return visit_change, insecurity_change


def run() -> None:
    panel, insecurity, profile = build_panel()
    visit_change, insecurity_change = build_change_tables(panel, insecurity)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    panel.to_csv(PROCESSED_DIR / "provincial_panel.csv", index=False)
    insecurity.to_csv(PROCESSED_DIR / "food_insecurity_trend.csv", index=False)
    profile.to_csv(PROCESSED_DIR / "national_client_profile.csv", index=False)
    visit_change.to_csv(PROCESSED_DIR / "provincial_visit_change_2019_2025.csv", index=False)
    insecurity_change.to_csv(
        PROCESSED_DIR / "provincial_food_insecurity_change_2019_2024.csv", index=False
    )
    print(f"Wrote {len(panel)} provincial-year rows")


if __name__ == "__main__":
    run()
