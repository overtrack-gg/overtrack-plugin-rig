# OverTrack Plugin Rig

This repository is designed to facilitate the development of OverTrack plugins, adding support for additional games.

To support an additional game, you must implement a HTTP/HTTPS server that runs locally and accepts an image+json data 
then returns the json data with any additional fields extracted through computer vision added.

## extract_frames
You may use `extract_frames.py` (or [`extract_frames.exe`](https://github.com/synap5e/overtrack-plugin-rig/releases)) 
to simulate OverTrack's posting of frames to your server. 

### Usage
```
usage: extract_frames.exe [-h] [--fps FPS] [--seek SEEK] source destination

positional arguments:
  source                video source to extract frames from
  destination           http endpoint to POST frames to

optional arguments:
  -h, --help            show this help message and exit
  --fps FPS, -r FPS     fps to extract frames at (can be decimal)
  --seek SEEK, -s SEEK  seek time in seconds to seek into input before
                        starting
```

### Example
```
python .\extract_frames.py -r 0.5 "M:\Videos\Best fractals zoom ever-BTiZD7p_oTc.mkv" http://localhost:5000
```

Note that extract_frames will POST frames as fast as they can be decoded from the video.
This is different from how the plugin will function under OverTrack, where frames will be posted in realtime.
Frames will still have correct `timestamp`s in the json data.

If you need frames to be posted in realtime (i.e. simulating the delay when running on a game), please submit an issue.

## Server

The server should be able to receive a POST to some endpoint, containing 2 files: `image` and `frame`.

### Request
`image` is a raw bytestream for a BGR 1920x1080 image. Specifically this means it will consist of `6220800` bytes.
Be careful of the BGR colorspace and whether your image processing library decodes as width,height or height,width.
For decoding this image under python, the following is correct
```python
    image = np.frombuffer(
        request.files['image'].read(), 
        dtype=np.uint8
    ).reshape((1080, 1920, 3))
```

`frame` is the extracted data from the image so far, and various metadata such as timestamp and frame number.
```json
{
    "timestamp": 1556855549.3732016,
    "timestamp_str": "2019/05/03 03:52:29.37",
    "relative_timestamp_str": "00:00:00.00",
    "relative_timestamp": 0.0,
    "frame_no": 51
}
```

Also included is the `source` field. This contains data specific to the source method. For `extract_frames` this consists 
of metadata specific to frame extraction from videos. When processing from a live game, `source` will instead contain
metadata regarding the display capture and process being captured.

### Response
The server should respond with a 200 status code, returning json content. 
The response MUST include all fields passed in the `frame` json unmodified, and may add additional fields that have been 
extracted from the image. Each top-level field should be its own object.

At this point `extract_frames` requires a 200 status code for each frame. 
In future support can be added for non-200 status codes to allow either reporting an error to the user, or to denote an 
error condition was hit during processing and request that the current image be uploaded to allow reproduction of the error.

While the server processing a frame is in-general stateless, it may optionally keep state for performance reasons.
For example, while some aspects of capture e.g. killfeed processing may need to run once every second, other aspects may
be more expensive but also not require as frequent processing. The server may keep state to allow it to only process frames
at a less frequent interval. Another option for performance is to keep track of some state of the game so that certain 
processors may be excluded from running if previous frames have shown that they are not required.
