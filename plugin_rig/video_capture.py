import os
import time
from typing import NamedTuple, Optional, Tuple, Iterable

import cv2
from tqdm import tqdm

from plugin_rig.frame import Frame
from plugin_rig.util import s2ts


class VideoFrameExtractor:

    class VideoFrameMetadata(NamedTuple):
        file: str
        video_fps: float
        video_frames: int
        extract_fps: int
        original_shape: Tuple[int]

    def __init__(self, path: str, extract_fps: float = 2, debug_frames: bool = False, seek: float = None, start_timestamp: float = None):
        self.path = path
        self.extract_fps = extract_fps
        self.debug = debug_frames
        if start_timestamp is not None:
            self.start_timestamp = start_timestamp
        else:
            self.start_timestamp = time.time()

        self.vid = cv2.VideoCapture(path)
        assert self.vid.isOpened()
        self.vid_fps = self.vid.get(cv2.CAP_PROP_FPS)
        self.vid_frames = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

        if seek:
            self.vid.set(cv2.CAP_PROP_POS_MSEC, int(seek * 1000))
            self.frame_no = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        else:
            self.frame_no = 0

        self.skipframes = int(self.vid_fps / self.extract_fps)

    def get(self) -> Optional[Frame]:
        r, frame = self.vid.read()
        timestamp = round(self.frame_no / self.vid_fps, 5)

        self.frame_no += 1
        if not r:
            return None

        for _ in range(self.skipframes):
            self.vid.grab()
            self.frame_no += 1

        original_shape = frame.shape
        if frame.shape != (1080, 1920, 3):
            frame = cv2.resize(frame, (1920, 1080))

        f = Frame.create(
            frame,
            self.start_timestamp + timestamp,
            relative_timestamp=timestamp,
            debug=self.debug,

            frame_no=self.frame_no,
            source=self.VideoFrameMetadata(
                self.path,
                self.vid_fps,
                int(self.vid_frames),
                int(self.extract_fps),
                original_shape
            )
        )
        return f

    def close(self) -> None:
        self.vid.release()

    def tqdm(self) -> Iterable[Frame]:
        bar = tqdm(total=int(self.vid_frames / self.vid_fps), unit_scale=True)
        last = 0
        while True:
            f = self.get()
            if not f:
                break

            bar.update((self.frame_no - last) / self.vid_fps)
            bar.set_description(f'{os.path.basename(self.path)} | {s2ts(self.frame_no / self.vid_fps)}/{s2ts(self.vid_frames / self.vid_fps)}')
            last = self.frame_no

            yield f
