# Store Intelligence System — Design Choices

## 1. Detection Model Choice

### Options considered:
- YOLOv8
- YOLOv9
- RT-DETR
- VLM-based detection (GPT-4V / Gemini Vision)

### AI suggestion:
Use RT-DETR or VLM for better occlusion handling.

### Final decision:
YOLOv8 + OpenCV tracking

### Reason:
- Real-time performance requirement
- Easier integration with tracking pipeline
- VLMs are too slow for frame-by-frame inference

### Tradeoff:
- Slightly weaker occlusion handling
- Much more stable runtime

---

## 2. Event Schema Design

### Options considered:
- Nested session-based schema
- Graph-based event model
- Flat event stream (selected)

### AI suggestion:
Use hierarchical session objects.

### Final decision:
Flat event schema with visitor_id grouping

### Reason:
- Easier ingestion and deduplication
- Works well with REST API
- Simplifies SQL queries for metrics

### Tradeoff:
- Less expressive than hierarchical model
- Requires careful session reconstruction

---

## 3. API Architecture Choice

### Options considered:
- FastAPI + SQLite (selected)
- FastAPI + PostgreSQL
- Kafka + stream processing pipeline

### AI suggestion:
Kafka-based event streaming system

### Final decision:
FastAPI + SQLite (Dockerized)

### Reason:
- Assignment explicitly requires docker compose simplicity
- Deterministic evaluation environment
- Avoids infrastructure overhead

### Tradeoff:
- Not scalable to high throughput production load
- But ideal for evaluation correctness

---

## 4. Additional Design Decision (Optional but important)

### Re-ID Strategy:
- Chose trajectory + spatial overlap instead of deep re-ID networks

Reason:
- Staff uniform + occlusion makes deep re-ID unreliable without training data
- Simpler heuristic performs more consistently in controlled CCTV setup