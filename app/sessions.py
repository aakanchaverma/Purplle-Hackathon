from collections import defaultdict
from datetime import datetime, timedelta

SESSION_GAP_MINUTES = 5


def parse_time(t):
    return datetime.fromisoformat(t.replace("Z", ""))


def build_sessions(events):
    """
    Groups events into sessions per visitor_id.
    New session starts if gap > SESSION_GAP_MINUTES or ENTRY event occurs.
    """

    events = sorted(events, key=lambda x: x["timestamp"])

    sessions = defaultdict(list)

    last_time = {}
    session_counter = defaultdict(int)

    for e in events:
        vid = e.get("visitor_id")
        if not vid:
            continue

        t = parse_time(e["timestamp"])

        new_session = False

        if vid not in last_time:
            new_session = True
        else:
            gap = t - last_time[vid]
            if gap > timedelta(minutes=SESSION_GAP_MINUTES):
                new_session = True

        if new_session:
            session_counter[vid] += 1

        e["session_id"] = f"{vid}_S{session_counter[vid]}"

        sessions[e["session_id"]].append(e)
        last_time[vid] = t

    return sessions