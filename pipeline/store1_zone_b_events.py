from ultralytics import YOLO
import cv2
import json
import uuid
from datetime import datetime

MODEL = YOLO("yolov8n.pt")

VIDEO_PATH = "videos/store1/zone_b.mp4"

STORE_ID = "STORE1"
CAMERA_ID = "ZONE_B"

OUTPUT_FILE = "data/store1_zone_b.jsonl"

FPS_FALLBACK = 30

EXIT_TIMEOUT_SECONDS = 3

MIN_DWELL_SECONDS = 10

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = FPS_FALLBACK

EXIT_TIMEOUT_FRAMES = int(
    fps * EXIT_TIMEOUT_SECONDS
)

MIN_DWELL_FRAMES = int(
    fps * MIN_DWELL_SECONDS
)

active_tracks = {}

events = []

frame_no = 0

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

    if results[0].boxes.id is not None:

        ids = results[0].boxes.id.cpu().numpy()

        for track_id in ids:

            track_id = int(track_id)

            if track_id not in active_tracks:

                active_tracks[track_id] = {

                    "enter_frame": frame_no,

                    "last_seen": frame_no,

                    "entered": False
                }

            else:

                active_tracks[
                    track_id
                ]["last_seen"] = frame_no

                frames_present = (
                    frame_no
                    - active_tracks[track_id]["enter_frame"]
                )

                if (
                    frames_present
                    >= MIN_DWELL_FRAMES
                    and
                    not active_tracks[track_id]["entered"]
                ):

                    active_tracks[
                        track_id
                    ]["entered"] = True

                    events.append({

                        "event_id":
                            str(uuid.uuid4()),

                        "store_id":
                            STORE_ID,

                        "camera_id":
                            CAMERA_ID,

                        "visitor_id":
                            f"VIS_{track_id}",

                        "event_type":
                            "ZONE_ENTER",

                        "timestamp":
                            datetime.utcnow()
                            .isoformat()
                    })

                    print(
                        f"ZONE ENTER: {track_id}"
                    )

    tracks_to_remove = []

    for track_id, info in active_tracks.items():

        missing_frames = (
            frame_no
            - info["last_seen"]
        )

        if (
            missing_frames
            > EXIT_TIMEOUT_FRAMES
        ):

            dwell_seconds = round(
                (
                    info["last_seen"]
                    - info["enter_frame"]
                ) / fps,
                2
            )

            if info["entered"]:

                events.append({

                    "event_id":
                        str(uuid.uuid4()),

                    "store_id":
                        STORE_ID,

                    "camera_id":
                        CAMERA_ID,

                    "visitor_id":
                        f"VIS_{track_id}",

                    "event_type":
                        "ZONE_EXIT",

                    "timestamp":
                        datetime.utcnow()
                        .isoformat(),

                    "dwell_seconds":
                        dwell_seconds
                })

                print(
                    f"ZONE EXIT: {track_id} "
                    f"DWELL={dwell_seconds}s"
                )

            tracks_to_remove.append(
                track_id
            )

    for track_id in tracks_to_remove:

        del active_tracks[track_id]

    frame_no += 1

cap.release()

for track_id, info in active_tracks.items():

    if not info["entered"]:
        continue

    dwell_seconds = round(
        (
            info["last_seen"]
            - info["enter_frame"]
        ) / fps,
        2
    )

    events.append({

        "event_id":
            str(uuid.uuid4()),

        "store_id":
            STORE_ID,

        "camera_id":
            CAMERA_ID,

        "visitor_id":
            f"VIS_{track_id}",

        "event_type":
            "ZONE_EXIT",

        "timestamp":
            datetime.utcnow()
            .isoformat(),

        "dwell_seconds":
            dwell_seconds
    })

with open(
    OUTPUT_FILE,
    "w"
) as f:

    for event in events:

        f.write(
            json.dumps(event)
            + "\n"
        )

print(
    "\nEvents generated:",
    len(events)
)