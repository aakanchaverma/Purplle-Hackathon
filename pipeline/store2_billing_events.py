from ultralytics import YOLO
import cv2
import json
import uuid
from datetime import datetime

MODEL = YOLO("yolov8n.pt")

VIDEO_PATH = "videos/store2/billing.mp4"

STORE_ID = "STORE2"
CAMERA_ID = "BILLING"

OUTPUT_FILE = "data/store2_billing_events.jsonl"

QUEUE_LINE_Y = 350
COUNTER_LINE_Y = 500

MIN_QUEUE_SECONDS = 3
FPS_FALLBACK = 30

FRAME_SKIP = 3   # 🔥 IMPORTANT FIX

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = FPS_FALLBACK

MIN_QUEUE_FRAMES = int(fps * MIN_QUEUE_SECONDS)

events = []
track_memory = {}

frame_no = 0

while True:

    success, frame = cap.read()
    if not success:
        break

    # 🔥 SKIP FRAMES TO PREVENT HANG
    if frame_no % FRAME_SKIP != 0:
        frame_no += 1
        continue

    results = MODEL.track(
        frame,
        persist=True,
        classes=[0],
        verbose=False
    )

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(boxes, ids):

            track_id = int(track_id)
            x1, y1, x2, y2 = box
            center_y = (y1 + y2) / 2

            if track_id not in track_memory:
                track_memory[track_id] = {
                    "queue_start": None,
                    "queue_sent": False,
                    "billing_sent": False,
                    "last_y": center_y
                }

            info = track_memory[track_id]

            previous_y = info["last_y"]

            # QUEUE
            if center_y < QUEUE_LINE_Y:

                if info["queue_start"] is None:
                    info["queue_start"] = frame_no
                else:
                    frames = frame_no - info["queue_start"]

                    if frames >= MIN_QUEUE_FRAMES and not info["queue_sent"]:

                        events.append({
                            "event_id": str(uuid.uuid4()),
                            "store_id": STORE_ID,
                            "camera_id": CAMERA_ID,
                            "visitor_id": f"VIS_{track_id}",
                            "event_type": "QUEUE_JOIN",
                            "timestamp": datetime.utcnow().isoformat(),
                            "zone_id": "QUEUE",
                            "confidence": 0.9
                        })

                        info["queue_sent"] = True

            # BILLING
            if (
                previous_y < COUNTER_LINE_Y
                and center_y >= COUNTER_LINE_Y
                and info["queue_sent"]
                and not info["billing_sent"]
            ):

                events.append({
                    "event_id": str(uuid.uuid4()),
                    "store_id": STORE_ID,
                    "camera_id": CAMERA_ID,
                    "visitor_id": f"VIS_{track_id}",
                    "event_type": "BILLING_ENTER",
                    "timestamp": datetime.utcnow().isoformat(),
                    "zone_id": "COUNTER",
                    "confidence": 0.9
                })

                info["billing_sent"] = True

            info["last_y"] = center_y

    frame_no += 1

cap.release()

with open(OUTPUT_FILE, "w") as f:
    for e in events:
        f.write(json.dumps(e) + "\n")

print("Events generated:", len(events))