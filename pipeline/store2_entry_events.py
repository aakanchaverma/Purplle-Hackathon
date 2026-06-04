from ultralytics import YOLO
import cv2
import json
import uuid
from datetime import datetime

MODEL = YOLO("yolov8n.pt")

VIDEO_PATH = "videos/store2/entry_b.mp4"

LINE_Y = 545

cap = cv2.VideoCapture(VIDEO_PATH)

track_memory = {}

events = []

while True:

    success, frame = cap.read()

    if not success:
        break

    results = MODEL.track(
        frame,
        persist=True,
        classes=[0],
        verbose=False
    )

    # RED ENTRY/EXIT LINE
    cv2.line(
        frame,
        (0, LINE_Y),
        (frame.shape[1], LINE_Y),
        (0, 0, 255),
        3
    )

    cv2.putText(
        frame,
        f"ENTRY/EXIT LINE Y={LINE_Y}",
        (20, LINE_Y - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()

        ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(
            boxes,
            ids
        ):

            x1, y1, x2, y2 = box

            center_x = int(
                (x1 + x2) / 2
            )

            center_y = int(
                (y1 + y2) / 2
            )

            track_id = int(track_id)

            cv2.rectangle(
                frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2
            )

            cv2.circle(
                frame,
                (center_x, center_y),
                6,
                (255, 0, 0),
                -1
            )

            cv2.putText(
                frame,
                f"ID {track_id}",
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            if track_id not in track_memory:

                track_memory[track_id] = {
                    "last_y": center_y,
                    "side": (
                        "TOP"
                        if center_y < LINE_Y
                        else "BOTTOM"
                    )
                }

                continue

            previous_side = track_memory[
                track_id
            ]["side"]

            current_side = (
                "TOP"
                if center_y < LINE_Y
                else "BOTTOM"
            )

            # ENTRY
            if (
                previous_side == "TOP"
                and current_side == "BOTTOM"
            ):

                print(
                    f"ENTRY: {track_id}"
                )

                events.append({

                    "event_id":
                        str(uuid.uuid4()),

                    "store_id":
                        "STORE2",

                    "camera_id":
                        "ENTRY_B",

                    "visitor_id":
                        f"VIS_{track_id}",

                    "event_type":
                        "ENTRY",

                    "timestamp":
                        datetime.utcnow().isoformat(),

                    "zone_id":
                        "ENTRY",

                    "is_staff":
                        False,

                    "confidence":
                        0.90
                })

            # EXIT
            elif (
                previous_side == "BOTTOM"
                and current_side == "TOP"
            ):

                print(
                    f"EXIT: {track_id}"
                )

                events.append({

                    "event_id":
                        str(uuid.uuid4()),

                    "store_id":
                        "STORE2",

                    "camera_id":
                        "ENTRY_B",

                    "visitor_id":
                        f"VIS_{track_id}",

                    "event_type":
                        "EXIT",

                    "timestamp":
                        datetime.utcnow().isoformat(),

                    "zone_id":
                        "ENTRY",

                    "is_staff":
                        False,

                    "confidence":
                        0.90
                })

            track_memory[
                track_id
            ]["last_y"] = center_y

            track_memory[
                track_id
            ]["side"] = current_side

    cv2.imshow(
        "Store2 Entry Debug",
        frame
    )

    key = cv2.waitKey(1)

    if key == 27:
        break

cap.release()

cv2.destroyAllWindows()

with open(
    "data/events_store2.jsonl",
    "w"
) as f:

    for event in events:

        f.write(
            json.dumps(event)
            + "\n"
        )

print(
    f"\nEvents generated: {len(events)}"
)