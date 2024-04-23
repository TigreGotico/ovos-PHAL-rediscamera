import struct
import click
import cv2
import numpy as np
import redis
from ovos_config import Configuration


class RedisCameraReader:

    def __init__(self, device_name: str):
        kwargs = Configuration().get("redis", {"host": "127.0.0.1", "port": 6379})
        self.r = redis.Redis(**kwargs)
        self.r.ping()
        self.name = "cam::" + device_name

    def get(self, name=None):
        """Retrieve Numpy array from Redis key 'n'"""
        encoded = self.r.get(name or self.name)
        h, w = struct.unpack('>II', encoded[:8])
        a = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h, w, 3)
        return a


def get_app(**kwargs):
    # imported here to make flask dependency optional
    # mjpeg server is not the main purpose of the plugin
    from flask import Flask, Response

    app = Flask(__name__)

    image_hub = RedisCameraReader(**kwargs)

    def _gen_frames(name=None):  # generate frame by frame from camera
        name = name or image_hub.name
        while True:
            frame = image_hub.get("cam::" + name)
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

    @app.route('/video_feed/<name>')
    def named_video_feed(name):
        return Response(_gen_frames(name), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app


@click.command()
@click.option('--camera-id', type=str, help='Name of the device running the camera.')
@click.option('--camera-index', default=0, type=int, help='Index of the camera to be used.')
def main(camera_id, camera_index):
    """Launch the PHALRedisCamera with specified configurations."""
    app = get_app(camera_index=camera_index,
                  device_name=camera_id)
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
