import argparse
import json

import requests

from plugin_rig.video_capture import VideoFrameExtractor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('source', metavar='source', type=str, help='video source to extract frames from')
    parser.add_argument('destination', metavar='destination', type=str, help='http endpoint to POST frames to')
    parser.add_argument('--fps', '-r', type=float, default=1, help='fps to extract frames at (can be decimal)')
    parser.add_argument('--seek', '-s', type=int, default=None, help='seek time in seconds to seek into input before starting')
    args = parser.parse_args()

    capture = VideoFrameExtractor(
        args.source,
        extract_fps=args.fps,
        debug_frames=False,
        seek=args.seek
    )
    session = requests.Session()
    for frame in capture.tqdm():
        image = frame.image
        frame.strip()
        r = session.post(
            args.destination,
            files={
                'image': ('image.raw', image.tobytes(), 'application/octet-stream'),
                'frame': ('frame.json', json.dumps(frame), 'application/json')
            }
        )
        r.raise_for_status()


if __name__ == '__main__':
    main()
