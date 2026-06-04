import json


def load_events(path, store_id=None):
    """
    Loads JSONL events safely.
    Optionally filters by store_id to avoid mixing stores.
    """

    events = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            # optional filtering
            if store_id is None or event.get("store_id") == store_id:
                events.append(event)

    return events