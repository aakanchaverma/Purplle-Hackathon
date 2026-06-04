
---

# ✅ `DESIGN.md`

```md
# Store Intelligence System — Design Document

## 1. System Overview

This system converts raw CCTV footage into structured retail intelligence. The design follows a pipeline architecture:

CCTV Video → Detection Layer → Event Stream → Ingestion API → Metrics Engine → Dashboard

Each stage is decoupled to allow independent scaling and debugging.

---

## 2. Detection Layer Design

### Approach
- Object detection using YOLO-based model
- Multi-object tracking using trajectory consistency
- Simple Re-ID using bounding box overlap + spatial continuity

### Why this design
A full deep Re-ID model would improve identity persistence but increases compute cost significantly. For retail analytics use-case, session-level identity (not long-term identity) is sufficient.

---

## 3. Event Schema Strategy

The event schema is designed around:

- Event-driven architecture (not frame-driven)
- Session-based grouping using visitor_id
- Explicit metadata separation

Key design decisions:
- event_id ensures idempotency
- visitor_id represents a single visit session (not a person lifetime identity)
- timestamp is derived from frame offset for replayability

Tradeoff:
We prioritize consistency over perfect identity tracking across stores.

---

## 4. Session & Funnel Logic

Session definition:
- Starts at ENTRY
- Ends at EXIT or inactivity timeout

Funnel stages:
Entry → Zone Visit → Billing Queue → Purchase

Deduplication:
- Re-entry creates new session only if EXIT occurred earlier
- Prevents inflating visitor count due to camera overlap or re-entrance noise

---

## 5. API Architecture Choice

### Choice: Stateless FastAPI + SQLite storage

We avoided a distributed DB (e.g., Kafka + Postgres) because:
- requirement is single-machine deploy via Docker Compose
- evaluation focuses on logic correctness, not scale infrastructure

Tradeoff:
- Not horizontally scalable
- But fully reproducible and deterministic for evaluation

---

## 6. Real-time Metrics Computation

Metrics are computed on-demand from stored events:

- Unique visitors = distinct visitor_id per store per time window
- Conversion rate = purchasers / visitors
- Dwell time = aggregated per zone
- Queue metrics = derived from BILLING_QUEUE_JOIN events

---

## 7. Anomaly Detection Logic

Rule-based detection used instead of ML due to:
- interpretability requirement
- deterministic scoring environment

Anomalies:
- Queue spike → sudden increase in queue_depth
- Conversion drop → deviation from baseline
- Dead zone → no zone activity for threshold period
- Stale feed → no events in 10 minutes

---

## 8. AI-Assisted Decisions

### Decision 1: Detection model
AI suggested transformer-based tracking; rejected due to latency and complexity.
Selected YOLO + lightweight tracking instead.

---

### Decision 2: Event schema
AI suggested nested schema for session hierarchy.
Rejected nested design due to ingestion complexity.
Chose flat schema for idempotent ingestion.

---

### Decision 3: API design
AI suggested event streaming via Kafka.
Rejected due to evaluation constraints.
Chose REST ingestion + in-memory/SQLite processing.

---

## 9. Failure Handling Strategy

- Missing camera feed → no crash, metrics degrade gracefully
- Zero traffic stores → return empty but valid JSON
- Partial ingestion failure → per-event rejection, not batch failure

---

## 10. Summary

The system prioritizes:
- Determinism over complexity
- Interpretability over black-box ML
- Reproducibility over distributed scale