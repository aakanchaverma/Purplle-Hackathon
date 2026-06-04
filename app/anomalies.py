def detect_anomalies(events):
    queue = 0
    entries = 0
    billing = 0

    for e in events:
        if e["event_type"] == "QUEUE_JOIN":
            queue += 1
        if e["event_type"] == "ENTRY":
            entries += 1
        if e["event_type"] == "BILLING_ENTER":
            billing += 1

    anomalies = []

    # Queue spike
    if queue > max(entries * 0.5, 5):
        anomalies.append({
            "type": "QUEUE_SPIKE",
            "severity": "WARN",
            "message": "High queue pressure detected",
            "suggestion": "Increase staffing at billing counter"
        })

    # Conversion drop
    conv = billing / max(entries, 1)
    if conv < 0.2:
        anomalies.append({
            "type": "CONVERSION_DROP",
            "severity": "CRITICAL",
            "message": "Low conversion rate detected",
            "suggestion": "Investigate billing delays or zone friction"
        })

    # Dead store
    if entries == 0:
        anomalies.append({
            "type": "NO_TRAFFIC",
            "severity": "CRITICAL",
            "message": "No store traffic detected",
            "suggestion": "Check camera feed or store inactivity"
        })

    return anomalies