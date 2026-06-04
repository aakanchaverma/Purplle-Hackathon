from fastapi import FastAPI
from app.models import Event

from app.event_loader import load_events
from app.metrics import entry_exit_metrics, zone_metrics, billing_metrics

from app.ingestion import save_events

from app.database import Base, engine

from sqlalchemy import func

from app.database import (
    SessionLocal,
    EventDB
)

from datetime import datetime

from app.database import (
    SessionLocal,
    EventDB
)

from collections import defaultdict

# In-memory event storage (temporary hack for hackathon)
store_events = defaultdict(list)

from app.funnel import compute_funnel
from app.heatmap import compute_heatmap
from app.anomalies import detect_anomalies

Base.metadata.create_all(engine)

app = FastAPI()

events = load_events("data/events_store2.jsonl")

@app.get("/")
def home():

    return {
        "message": "Store Intelligence API Running"
    }

@app.post("/events/ingest")
def ingest(events: list[Event]):

    stored = save_events(events)

    return {

        "received": len(events),

        "stored": stored
    }

@app.post("/events/ingest")
def ingest_events(payload: list[dict]):
    """
    Accepts batch of events and stores them in memory.
    """

    for event in payload:
        store_id = event.get("store_id")

        if not store_id:
            continue

        store_events[store_id].append(event)

    return {
        "status": "success",
        "ingested": len(payload)
    }

@app.get("/stores/{store_id}/metrics")
def metrics(store_id: str):

    db = SessionLocal()

    events = db.query(EventDB).filter(
        EventDB.store_id == store_id
    ).all()

    if not events:

        return {

            "store_id": store_id,

            "unique_visitors": 0,

            "conversion_rate": 0,

            "avg_dwell_ms": 0,

            "queue_depth": 0,

            "abandonment_rate": 0
        }

    visitors = set()

    dwell_values = []

    queue_count = 0

    abandon_count = 0

    converted_visitors = set()

    for e in events:

        visitors.add(
            e.visitor_id
        )

        if e.dwell_ms:

            dwell_values.append(
                e.dwell_ms
            )

        if (
            e.event_type
            ==
            "BILLING_QUEUE_JOIN"
        ):

            queue_count += 1

        if (
            e.event_type
            ==
            "BILLING_QUEUE_ABANDON"
        ):

            abandon_count += 1

        if (
            e.event_type
            ==
            "PURCHASE"
        ):

            converted_visitors.add(
                e.visitor_id
            )

    unique_visitors = len(
        visitors
    )

    conversion_rate = 0

    if unique_visitors > 0:

        conversion_rate = round(

            len(converted_visitors)
            /
            unique_visitors
            *
            100,

            2
        )

    avg_dwell = 0

    if dwell_values:

        avg_dwell = round(

            sum(dwell_values)
            /
            len(dwell_values),

            2
        )

    abandonment_rate = 0

    if queue_count > 0:

        abandonment_rate = round(

            abandon_count
            /
            queue_count
            *
            100,

            2
        )

    return {

        "store_id":
            store_id,

        "unique_visitors":
            unique_visitors,

        "conversion_rate":
            conversion_rate,

        "avg_dwell_ms":
            avg_dwell,

        "queue_depth":
            queue_count,

        "abandonment_rate":
            abandonment_rate
    }

@app.get("/health")
def health():

    db = SessionLocal()

    latest = db.query(
        EventDB
    ).order_by(
        EventDB.timestamp.desc()
    ).first()

    if not latest:

        return {

            "status":
                "NO_EVENTS",

            "warning":
                "STALE_FEED"
        }

    try:

        event_time = datetime.fromisoformat(
            latest.timestamp.replace(
                "Z",
                ""
            )
        )

        age_minutes = (

            datetime.utcnow()
            -
            event_time

        ).total_seconds() / 60

    except:

        age_minutes = 0

    warning = None

    if age_minutes > 10:

        warning = "STALE_FEED"

    return {

        "status":
            "healthy",

        "last_event_timestamp":
            latest.timestamp,

        "minutes_since_last_event":
            round(age_minutes, 2),

        "warning":
            warning
    }

@app.get("/debug/events")
def debug_events():

    db = SessionLocal()

    rows = db.query(
        EventDB
    ).all()

    result = []

    for r in rows:

        result.append({

            "event_id":
                r.event_id,

            "store_id":
                r.store_id,

            "visitor_id":
                r.visitor_id,

            "event_type":
                r.event_type
        })

    return result

@app.get("/health")
def health():
    return {"status": "ok", "events_loaded": len(events)}


@app.get("/stores/STORE2/metrics")
def metrics():
    return {
        "entry_metrics": entry_exit_metrics(events),
        "zone_metrics": zone_metrics(events),
        "billing_metrics": billing_metrics(events)
    }

@app.get("/stores/{store_id}/funnel")
def funnel(store_id: str):
    events = store_events[store_id]
    return compute_funnel(events)


@app.get("/stores/{store_id}/heatmap")
def heatmap(store_id: str):
    events = store_events[store_id]
    return compute_heatmap(events)


@app.get("/stores/{store_id}/anomalies")
def anomalies(store_id: str):
    events = store_events[store_id]
    return detect_anomalies(events)