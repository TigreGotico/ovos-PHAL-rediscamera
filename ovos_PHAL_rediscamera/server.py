import struct

import cv2
import numpy as np
import redis
from flask import Flask, Response


class RedisCameraReader:

    def __init__(self, name, host, port=6379,  **kwargs):
        # Redis connection
        kwargs = {k: v for k,v in kwargs.items()
                  if k in ["username", "password", "ssl",
                           "ssl_certfile", "ssl_keyfile", "ssl_ca_certs"]}
        self.r = redis.Redis(host=host, port=port, **kwargs)
        self.r.ping()
        self.name = name

    def get(self):
        """Retrieve Numpy array from Redis key 'n'"""
        encoded = self.r.get(self.name)
        h, w = struct.unpack('>II', encoded[:8])
        a = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h, w, 3)
        return a


def get_app(**kwargs):
    app = Flask(__name__)

    image_hub = RedisCameraReader(**kwargs)

    def _gen_frames():  # generate frame by frame from camera
        while True:
            frame = image_hub.get()
            if frame is None:
                continue
            try:
                ret, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            except Exception as e:
                pass

    @app.route('/video_feed')
    def video_feed():
        return Response(_gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app


def main(conf=None):
    app = get_app(**conf)
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    # TODO kwargs
    conf = {
        "name": "laptop",
        "host": "192.168.1.17"
    }
    main(conf)
