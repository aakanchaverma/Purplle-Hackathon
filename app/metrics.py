def entry_exit_metrics(events):
    entries = sum(1 for e in events if e["event_type"] == "ENTRY")
    exits = sum(1 for e in events if e["event_type"] == "EXIT")

    return {"entries": entries, "exits": exits}


def zone_metrics(events):
    enters = sum(1 for e in events if e["event_type"] == "ZONE_ENTER")

    dwell_times = [
        e.get("dwell_seconds", 0)
        for e in events
        if e["event_type"] == "ZONE_EXIT"
    ]

    avg_dwell = round(sum(dwell_times) / len(dwell_times), 2) if dwell_times else 0

    return {
        "zone_visits": enters,
        "avg_dwell_seconds": avg_dwell
    }


def billing_metrics(events):
    queue_count = sum(1 for e in events if e["event_type"] == "QUEUE_JOIN")
    billing_count = sum(1 for e in events if e["event_type"] == "BILLING_ENTER")

    return {
        "queue_count": queue_count,
        "billing_count": billing_count
    }


def compute_conversion_rate(events):
    sessions_with_billing = set()

    for e in events:
        if e["event_type"] == "BILLING_ENTER":
            sessions_with_billing.add(e.get("visitor_id"))

    sessions_total = set(
        e.get("visitor_id")
        for e in events
        if e.get("visitor_id")
    )

    if not sessions_total:
        return 0.0

    return round(len(sessions_with_billing) / len(sessions_total), 2)