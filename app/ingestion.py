import json

from app.database import (
    SessionLocal,
    EventDB
)


def save_events(events):

    db = SessionLocal()

    stored = 0

    for event in events:

        existing = db.get(
            EventDB,
            event.event_id
        )

        if existing:
            continue

        row = EventDB(

            event_id=event.event_id,

            store_id=event.store_id,

            camera_id=event.camera_id,

            visitor_id=event.visitor_id,

            event_type=event.event_type,

            timestamp=event.timestamp,

            zone_id=event.zone_id,

            dwell_ms=event.dwell_ms,

            is_staff=event.is_staff,

            confidence=event.confidence,

            metadata_json=json.dumps(
                event.metadata
            )
        )

        db.add(row)

        stored += 1

    db.commit()

    db.close()

    return stored