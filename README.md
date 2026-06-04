# Store Intelligence System

## Overview
This project implements an end-to-end Store Intelligence pipeline that processes CCTV footage, generates structured behavioral events, ingests them into a FastAPI-based analytics system, and exposes real-time retail metrics.

The system simulates a production-grade offline analytics engine for physical retail stores.

---

## System Architecture

The system is divided into three layers:

1. Detection Pipeline
   - Processes CCTV frames
   - Performs object detection + tracking
   - Assigns visitor IDs
   - Emits structured events

2. Intelligence API
   - Ingests events
   - Deduplicates using event_id
   - Computes real-time metrics, funnel, anomalies
   - Exposes REST endpoints

3. Dashboard (Streamlit)
   - Displays live store metrics
   - Connects to API endpoints

---

## Tech Stack

- Python 3.10
- FastAPI
- Streamlit
- YOLO (Ultralytics)
- OpenCV
- SQLite (via SQLAlchemy)
- Docker Compose

---

## How to Run

### 1. Start system
```bash
docker compose up --build