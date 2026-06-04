import json
from collections import Counter

from collections import defaultdict
from datetime import datetime

def hourly_distribution(events):
    hours = defaultdict(int)

    for e in events:
        t = datetime.fromisoformat(e["timestamp"])
        hours[t.hour] += 1

    return dict(hours)

# -----------------------------
# LOAD EVENTS
# -----------------------------
def load_events(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]


# -----------------------------
# METRICS
# -----------------------------
def entry_exit_metrics(events):
    return {
        "entries": sum(1 for e in events if e["event_type"] == "ENTRY"),
        "exits": sum(1 for e in events if e["event_type"] == "EXIT")
    }


def zone_metrics(events):
    enters = [e for e in events if "ENTER" in e["event_type"]]
    exits = [e for e in events if "EXIT" in e["event_type"] and "dwell_seconds" in e]

    avg_dwell = (
        sum(e["dwell_seconds"] for e in exits) / len(exits)
        if exits else 0
    )

    return {
        "zone_visits": len(enters),
        "avg_dwell_seconds": round(avg_dwell, 2)
    }


def billing_metrics(events):
    return {
        "queue_count": sum(1 for e in events if e["event_type"] == "QUEUE_JOIN"),
        "billing_count": sum(1 for e in events if e["event_type"] == "BILLING_ENTER")
    }


# -----------------------------
# LOAD DATA
# -----------------------------
entry_events = load_events("data/events_store2.jsonl")
zone_events = load_events("data/store2_zone.jsonl")
billing_events = load_events("data/store2_billing_events.jsonl")

all_events = entry_events + zone_events + billing_events


# -----------------------------
# RUN METRICS
# -----------------------------
entry_metrics = entry_exit_metrics(entry_events)
zone_metrics = zone_metrics(zone_events)
billing_metrics = billing_metrics(billing_events)

counter = Counter(e["event_type"] for e in all_events)


# -----------------------------
# FINAL OUTPUT (IMPORTANT FOR STREAMLIT)
# -----------------------------
result = {
    "entry_metrics": entry_metrics,
    "zone_metrics": zone_metrics,
    "billing_metrics": billing_metrics,
    "event_type_summary": dict(counter),
    "business_insights": {
        "queue_pressure": billing_metrics["queue_count"],
        "zone_engagement": zone_metrics["zone_visits"],
        
        "conversion_rate": round(
            billing_metrics["billing_count"] / max(billing_metrics["queue_count"], 1),
            2
        ),
        "system_assumption_note": (
            "Each camera operates independently without temporal synchronization. "
            "Analytics are computed per stream and aggregated at dashboard level; "
            "cross-camera identity matching is not performed."
        )
    }
}

print(json.dumps(result, indent=2))

with open("analytics_output.json", "w") as f:
    json.dump(result, f, indent=2)

print("Billing sample:", billing_events[:3])
print("Billing event types:", set(e["event_type"] for e in billing_events))