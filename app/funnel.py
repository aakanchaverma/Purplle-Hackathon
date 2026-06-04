from collections import defaultdict

def compute_funnel(events):
    visitors = set()
    entry = set()
    zone = set()
    billing_queue = set()
    purchase = set()

    for e in events:
        vid = e.get("visitor_id")
        visitors.add(vid)

        if e["event_type"] == "ENTRY":
            entry.add(vid)

        elif e["event_type"] == "ZONE_ENTER":
            zone.add(vid)

        elif e["event_type"] == "QUEUE_JOIN":
            billing_queue.add(vid)

        elif e["event_type"] == "BILLING_ENTER":
            purchase.add(vid)

    total = len(visitors) if visitors else 1

    return {
        "entry": len(entry),
        "zone": len(zone),
        "billing_queue": len(billing_queue),
        "purchase": len(purchase),
        "dropoff": {
            "entry_to_zone": round((len(entry)-len(zone))/total, 2),
            "zone_to_queue": round((len(zone)-len(billing_queue))/total, 2),
            "queue_to_purchase": round((len(billing_queue)-len(purchase))/total, 2)
        }
    }