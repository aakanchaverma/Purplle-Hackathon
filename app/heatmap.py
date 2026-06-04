from collections import defaultdict

def compute_heatmap(events):
    zone_counts = defaultdict(int)
    dwell_map = defaultdict(list)

    for e in events:
        zone = e.get("zone_id", "UNKNOWN")

        if e["event_type"] == "ZONE_ENTER":
            zone_counts[zone] += 1

        if e["event_type"] == "ZONE_EXIT":
            dwell_map[zone].append(e.get("dwell_ms", 0))

    heatmap = {}

    for z in zone_counts:
        avg_dwell = sum(dwell_map[z]) / max(len(dwell_map[z]), 1)
        heatmap[z] = {
            "visit_score": zone_counts[z],
            "avg_dwell": round(avg_dwell, 2)
        }

    return heatmap