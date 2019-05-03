import json
import pprint
import queue
from threading import Thread

from flask import Flask, Response, request
import numpy as np
import cv2

app = Flask('test_server')

q = queue.Queue()


@app.route('/', methods=['POST'])
def root():
    image = np.frombuffer(request.files['image'].read(), dtype=np.uint8).reshape((1080, 1920, 3))
    frame = json.load(request.files['frame'])

    pprint.pprint(frame)
    q.put(image)

    return Response(
        status=200,
        response=json.dumps(frame)
    )


def main() -> None:
    Thread(target=app.run).start()
    while True:
        image = q.get()
        cv2.imshow('frame', image)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
