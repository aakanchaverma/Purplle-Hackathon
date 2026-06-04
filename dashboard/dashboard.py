import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st
import pandas as pd

from app.event_loader import load_events
from app.metrics import (
    entry_exit_metrics,
    zone_metrics,
    billing_metrics
)

# ==============================
# SAFE CONVERSION FUNCTION
# ==============================
def compute_conversion_rate(entry_events, billing_events):
    entries = len(entry_events)
    billing = len(billing_events)

    # prevent division error + keep stable definition
    return round(billing / max(entries, 1), 2)

# ==============================
# STREAMLIT CONFIG
# ==============================
st.set_page_config(
    page_title="Purplle Store Intelligence",
    layout="wide"
)

st.title("Purplle Store Intelligence Dashboard")

# ==============================
# LOAD EVENTS
# ==============================

entry_events = load_events("data/events_store2.jsonl")

zone_a_events = load_events("data/store1_zone_a.jsonl")
zone_b_events = load_events("data/store1_zone_b.jsonl")
store2_zone_events = load_events("data/store2_zone.jsonl")

billing_events = load_events("data/store2_billing_events.jsonl")

# ==============================
# CORE METRICS
# ==============================

entry_data = entry_exit_metrics(entry_events)

zone_a_data = zone_metrics(zone_a_events)
zone_b_data = zone_metrics(zone_b_events)
store2_zone_data = zone_metrics(store2_zone_events)

billing_data = billing_metrics(billing_events)

conversion_rate = compute_conversion_rate(entry_events, billing_events)

# ==============================
# TOP KPI ROW
# ==============================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Entries", entry_data["entries"])

with col2:
    st.metric("Exits", entry_data["exits"])

with col3:
    st.metric("Queue Count", billing_data["queue_count"])

with col4:
    st.metric("Billing Count", billing_data["billing_count"])

st.divider()

# ==============================
# ZONE ANALYTICS TABLE
# ==============================

zone_df = pd.DataFrame({
    "Zone": ["Store1 Zone A", "Store1 Zone B", "Store2 Zone"],
    "Visits": [
        zone_a_data["zone_visits"],
        zone_b_data["zone_visits"],
        store2_zone_data["zone_visits"]
    ],
    "Average Dwell (sec)": [
        zone_a_data["avg_dwell_seconds"],
        zone_b_data["avg_dwell_seconds"],
        store2_zone_data["avg_dwell_seconds"]
    ]
})

st.subheader("Zone Analytics")
st.dataframe(zone_df, use_container_width=True)

# ==============================
# VISUALIZATIONS
# ==============================

st.subheader("Zone Visits")
st.bar_chart(zone_df.set_index("Zone")["Visits"])

st.subheader("Average Dwell Time")
st.bar_chart(zone_df.set_index("Zone")["Average Dwell (sec)"])

# ==============================
# RAW METRICS (NO LOSS OF DATA)
# ==============================

st.subheader("Raw Metrics")

st.json({
    "entry_metrics": entry_data,
    "zone_a_metrics": zone_a_data,
    "zone_b_metrics": zone_b_data,
    "store2_zone_metrics": store2_zone_data,
    "billing_metrics": billing_data,
    "conversion_rate": conversion_rate
})

st.divider()

# ==============================
# INSIGHTS ENGINE (FIXED LOGIC)
# ==============================

st.header("AI Business Insights")

# stable engagement score (no random weighting changes later)
zone_df["engagement_score"] = (
    zone_df["Visits"] * 0.5 +
    zone_df["Average Dwell (sec)"] * 0.5
)

best_zone = zone_df.loc[zone_df["engagement_score"].idxmax()]
worst_zone = zone_df.loc[zone_df["engagement_score"].idxmin()]

st.subheader("Zone Performance Insights")

st.write(
    f"Best engagement zone: {best_zone['Zone']} "
    f"with {best_zone['Visits']} visits."
)

st.write(
    f"Lowest engagement zone: {worst_zone['Zone']} "
    f"with {worst_zone['Visits']} visits."
)

# ==============================
# DWELL INSIGHTS
# ==============================

highest_dwell = zone_df.loc[
    zone_df["Average Dwell (sec)"].idxmax()
]

st.subheader("Dwell Time Insights")

st.write(
    f"Most dwell time: {highest_dwell['Zone']} "
    f"({highest_dwell['Average Dwell (sec)']} sec)"
)

# ==============================
# TRAFFIC INSIGHTS
# ==============================

st.subheader("Store Traffic Insights")

entry_gap = entry_data["entries"] - entry_data["exits"]

st.write(f"Entry-Exit Gap: {entry_gap}")
st.write(f"Conversion Rate: {conversion_rate}")

# ==============================
# BILLING INSIGHTS
# ==============================

st.subheader("Billing Insights")

st.write(f"Queue Events: {billing_data['queue_count']}")
st.write(f"Billing Events: {billing_data['billing_count']}")

queue_pressure = billing_data["queue_count"] / max(entry_data["entries"], 1)
st.write(f"Queue Pressure Index: {round(queue_pressure, 2)}")

efficiency = billing_data["billing_count"] / max(entry_data["entries"], 1)
st.write(f"Store Efficiency: {round(efficiency, 2)}")

# ==============================
# RECOMMENDATIONS (RULE BASED)
# ==============================

st.subheader("Recommendations")

if zone_b_data["zone_visits"] > zone_a_data["zone_visits"]:
    st.success("Zone B shows higher traffic → optimize premium placement.")

if zone_a_data["avg_dwell_seconds"] > 20:
    st.success("Zone A high dwell time → strong engagement zone.")

if billing_data["queue_count"] > 5:
    st.warning("Queue buildup detected → staffing adjustment needed.")

# ==============================
# DATA QUALITY NOTE (IMPORTANT FOR HACKATHON)
# ==============================

st.info(
    "Note: Metrics are derived from asynchronous CCTV feeds. "
    "Zone-level signals reflect engagement trends, not absolute synchronized counts."
)
