import os
import io
import tempfile
from typing import List
import cv2
from PIL import Image
from app.core.processors.image_processor import PageImage, _to_jpeg


def extract_frames(
    file_bytes: bytes,
    max_seconds: int = 60,
    fps: int = 1,
) -> List[PageImage]:
    """
    Extract frames from a video at `fps` frames per second.
    Caps at max_seconds * fps total frames.
    Returns PageImage list (page_num = frame number, source_type='video').
    """
    max_frames = max_seconds * fps

    # Write to a temp file — OpenCV requires a file path
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    frames: List[PageImage] = []
    try:
        cap = cv2.VideoCapture(tmp_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
        frame_interval = max(1, int(video_fps / fps))

        frame_idx = 0
        captured = 0

        while cap.isOpened() and captured < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                # BGR → RGB
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
                jpeg = _to_jpeg(pil_img, quality=80)
                h, w = frame.shape[:2]
                frames.append(PageImage(
                    page_num=captured + 1,
                    image_bytes=jpeg,
                    width=w,
                    height=h,
                    source_type="video",
                ))
                captured += 1

            frame_idx += 1

        cap.release()
    finally:
        os.unlink(tmp_path)

    return frames
