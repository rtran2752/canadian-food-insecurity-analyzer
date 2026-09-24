import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import PROCESSED_DIR
from src.pipeline import run

st.set_page_config(page_title="Canada Food Access Monitor", page_icon="🍁", layout="wide")


@st.cache_data
def load_data():
    target = PROCESSED_DIR / "provincial_panel.csv"
    if not target.exists():
        run()
    panel = pd.read_csv(target)
    insecurity = pd.read_csv(PROCESSED_DIR / "food_insecurity_trend.csv")
    profile = pd.read_csv(PROCESSED_DIR / "national_client_profile.csv")
    visit_change = pd.read_csv(PROCESSED_DIR / "provincial_visit_change_2019_2025.csv")
    insecurity_change = pd.read_csv(
        PROCESSED_DIR / "provincial_food_insecurity_change_2019_2024.csv"
    )
    return panel, insecurity, profile, visit_change, insecurity_change


panel, insecurity, profile, visit_change, insecurity_change = load_data()
visits = panel.dropna(subset=["total_visits"]).copy()
st.title("🍁 Canada Food Access Monitor")
st.caption("Real public data from Food Banks Canada and Statistics Canada estimates republished by PROOF")
st.info("HungerCount measures visits during March—not unique people or average monthly demand. Food insecurity is a separate population survey measure.")

with st.sidebar:
    provinces = st.multiselect("Province", sorted(visits.province.unique()),
                               default=sorted(visits.province.unique()))
    chosen = visits[visits.province.isin(provinces)]

overview, insecurity_tab, relationship, people, methods = st.tabs(
    ["Food-bank demand", "Food insecurity", "Compare measures", "Who uses food banks", "Sources & limits"]
)

with overview:
    comparable_change = visit_change[visit_change.comparable_to_2019.astype(bool)]
    top_absolute = comparable_change.loc[comparable_change.absolute_change.idxmax()]
    top_percent = comparable_change.loc[comparable_change.percent_change.idxmax()]
    st.subheader("What the data show")
    a, b = st.columns(2)
    a.success(
        f"**Largest absolute increase:** {top_absolute.province} added "
        f"{top_absolute.absolute_change:,.0f} March visits from 2019 to 2025 "
        f"({top_absolute.percent_change:+.1f}%)."
    )
    b.success(
        f"**Largest percentage increase:** {top_percent.province} rose "
        f"{top_percent.percent_change:+.1f}%—an increase of "
        f"{top_percent.absolute_change:,.0f} visits."
    )
    latest = chosen[chosen.year == 2025]
    prior = chosen[chosen.year == 2024]
    c1, c2, c3 = st.columns(3)
    c1.metric("March 2025 visits", f"{latest.total_visits.sum():,.0f}")
    change = (latest.total_visits.sum() / prior.total_visits.sum() - 1) * 100 if len(prior) else float("nan")
    c2.metric("Change from 2024", f"{change:+.1f}%")
    c3.metric("Child visits", f"{latest.child_visits.sum():,.0f}")
    trend = chosen.groupby("year", as_index=False)[["total_visits", "child_visits"]].sum()
    long = trend.melt("year", var_name="measure", value_name="visits")
    st.plotly_chart(px.line(long, x="year", y="visits", color="measure", markers=True,
                            title="March HungerCount visits"), width="stretch")
    rank = latest.sort_values("total_visits", ascending=False)
    st.plotly_chart(px.bar(rank, x="province_code", y="total_visits", color="child_share_pct",
                           title="March 2025 visits by province",
                           labels={"child_share_pct": "Child share (%)"}), width="stretch")
    growth = latest[latest.comparable_to_2019.astype(bool)].sort_values("change_since_2019_pct")
    st.plotly_chart(px.bar(growth, x="change_since_2019_pct", y="province", orientation="h",
                           title="Change in visits, 2019–2025 (comparable provinces only)",
                           labels={"change_since_2019_pct": "Change (%)"}), width="stretch")
    st.subheader("Provincial comparison table")
    display_change = comparable_change[
        ["province", "visits_2019", "visits_2025", "absolute_change", "percent_change"]
    ].copy()
    st.dataframe(
        display_change.style.format({
            "visits_2019": "{:,.0f}", "visits_2025": "{:,.0f}",
            "absolute_change": "{:+,.0f}", "percent_change": "{:+.1f}%"
        }), width="stretch", hide_index=True
    )
    st.caption("Manitoba is excluded because Food Banks Canada flags its 2019 comparison as non-comparable.")

with insecurity_tab:
    top_fi_change = insecurity_change.iloc[0]
    st.success(
        f"**Largest increase, 2019–2024:** {top_fi_change.province} rose "
        f"{top_fi_change.percentage_point_change:+.1f} percentage points, from "
        f"{top_fi_change.food_insecurity_2019_pct:.1f}% to "
        f"{top_fi_change.food_insecurity_2024_pct:.1f}%."
    )
    fi = insecurity[insecurity.province.isin(provinces)]
    st.plotly_chart(px.line(fi, x="year", y="food_insecurity_pct", color="province",
                            markers=True, title="People living in food-insecure households",
                            labels={"food_insecurity_pct": "People (%)"}), width="stretch")
    latest_fi = fi[fi.year == 2024].sort_values("food_insecurity_pct", ascending=False)
    st.plotly_chart(px.bar(latest_fi, x="province_code", y="food_insecurity_pct",
                           title="Food insecurity by province, 2024",
                           labels={"food_insecurity_pct": "People (%)"}), width="stretch")
    st.dataframe(
        insecurity_change[["province", "food_insecurity_2019_pct",
                           "food_insecurity_2024_pct", "percentage_point_change"]]
        .style.format({
            "food_insecurity_2019_pct": "{:.1f}%",
            "food_insecurity_2024_pct": "{:.1f}%",
            "percentage_point_change": "{:+.1f} pp",
        }), width="stretch", hide_index=True
    )

with relationship:
    joined = panel.dropna(subset=["total_visits", "food_insecurity_pct"])
    joined = joined[joined.province.isin(provinces)]
    st.subheader("Two related—but different—signals")
    st.caption("Only 2019 and 2024 overlap. This chart is descriptive and does not establish causation or predictive accuracy.")
    st.plotly_chart(px.scatter(joined, x="food_insecurity_pct", y="total_visits",
                               color="province_code", symbol="year", hover_name="province",
                               title="Food insecurity and March food-bank visits",
                               labels={"food_insecurity_pct": "People in food-insecure households (%)"}),
                    width="stretch")
    st.dataframe(joined[["year", "province", "food_insecurity_pct", "total_visits",
                         "child_share_pct", "reporting_food_banks"]].sort_values(
                             ["year", "total_visits"], ascending=[False, False]),
                 width="stretch", hide_index=True)

with people:
    metrics = {
        "job_income_pct": "Employment as main income",
        "social_assistance_pct": "Social assistance",
        "market_rental_pct": "Market rental housing",
        "seniors_pct": "Seniors",
        "children_pct": "Children",
        "single_people_pct": "Single-person households",
    }
    long_profile = profile.melt("year", value_vars=list(metrics), var_name="group", value_name="percent")
    long_profile["group"] = long_profile.group.map(metrics)
    st.plotly_chart(px.line(long_profile, x="year", y="percent", color="group", markers=True,
                            title="National profile of food-bank clients",
                            labels={"percent": "Share (%)"}), width="stretch")

with methods:
    st.markdown("""
### Sources

- Food Banks Canada, **HungerCount 2019**, provincial table p. 11.
- Food Banks Canada, **HungerCount 2024**, provincial table p. 23.
- Food Banks Canada, **HungerCount 2025**, provincial table p. 28.
- Statistics Canada Canadian Income Survey estimates, republished in PROOF's downloadable chart dataset.

### Interpretation limits

- HungerCount is a cross-sectional census-style snapshot for March; it is not a monthly time series.
- A visit is not a unique person. One household can generate several visits.
- Demand is constrained by food-bank capacity, service rules, and reporting coverage.
- Manitoba's network structure and collection methods changed, so its 2019 comparison is suppressed.
- Food insecurity and food-bank use are not interchangeable: many food-insecure people never use food banks.
- Provincial totals are affected by population size. This project does not claim causal relationships.
- No forecast is presented because three HungerCount years are insufficient for a defensible provincial model.
""")
