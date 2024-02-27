import struct
from threading import Thread, Event

import cv2
import redis
from ovos_plugin_manager.templates.phal import PHALPlugin
from ovos_utils import create_daemon

from ovos_PHAL_rediscamera.server import get_app


class RedisStream(Thread):
    def __init__(self, name, host, camera_index=0, port=6379, **kwargs):
        super().__init__(daemon=True)
        self.stream = cv2.VideoCapture(camera_index)
        # Redis connection
        kwargs = {k: v for k, v in kwargs.items()
                  if k in ["username", "password", "ssl",
                           "ssl_certfile", "ssl_keyfile", "ssl_ca_certs"]}
        self.r = redis.Redis(host=host, port=port, **kwargs)
        self.r.ping()
        self.name = name
        self.stopped = Event()

    def run(self):
        while not self.stopped.is_set():
            (self.grabbed, self.frame) = self.stream.read()
            h, w = self.frame.shape[:2]
            shape = struct.pack('>II', h, w)
            encoded = shape + self.frame.tobytes()
            # Store encoded data in Redis
            self.r.set(self.name, encoded)

    def stop(self):
        self.stopped.set()


class PHALRedisCamera(PHALPlugin):
    def __init__(self, bus, name="phal_rediscamera", config=None):
        config = config or {}
        if "host" not in config:
            raise ValueError("redis2mjpeg server host not set in config")
        self.sender = RedisStream(**config)
        super().__init__(bus, name, config or {})
        if config.get("serve_mjpeg"):
            self.server = create_daemon(self.serve_mjpeg)
        else:
            self.server = None

    def serve_mjpeg(self):
        app = get_app(**self.config)
        app.run(host="0.0.0.0")

    def run(self):
        self.sender.run()

    def shutdown(self):
        self.sender.stop()
        if self.server:
            self.server.join(0)
