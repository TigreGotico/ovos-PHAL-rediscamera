# PHAL redis camera

Expose your OVOS device camera to Redis for remote processing

When you need to access a camera feed in several devices

> This plugin needs a redis server running, it will use it to store the most recent camera frame, it is suitable for when you need to process the camera in several devices


## Redis Server

You can find dedicated redis documentation elsewhere, the easiest way to get started is with docker

`docker run -p 6379:6379 --name redis -d redis`

## Configuration

```javascript
{
  "PHAL": {
    "ovos-PHAL-rediscamera": {
      "device_name": "my_phal_device",
      "camera_index": 0,
      "serve_mjpeg": false, // serve a mjpeg camera stream at http://0.0.0.0:5000/video_feed
      "host": "my-redis.cloud.redislabs.com",
      // below are all optional redis options
      "port": 6379,
      "username": "default", // use your Redis user. More info https://redis.io/docs/management/security/acl/
      "password": "secret", // use your Redis password
      "ssl": true,
      "ssl_certfile": "./redis_user.crt",
      "ssl_keyfile": "./redis_user_private.key",
      "ssl_ca_certs": "./redis_ca.pem"
    }
  }
}
```

## Home Assistant

You can use the `"serve_mjpeg"` option to integrate this camera [into Home Assistant](https://www.home-assistant.io/integrations/mjpeg/)

![img.png](img.png)

## Consuming the Feed

You can consume a redis camera feed from any device with access to the redis server

```python
import struct
import numpy as np
import redis


class RedisCameraReader:
    def __init__(self, name, host, port=6379):
        # Redis connection
        self.r = redis.Redis(host=host, port=port)
        self.r.ping()
        self.name = name

    def get(self):
        """Retrieve Numpy array from Redis camera 'self.name' """
        encoded = self.r.get(self.name)
        h, w = struct.unpack('>II', encoded[:8])
        a = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h, w, 3)
        return a


remote_cam = RedisCameraReader("laptop", "192.168.1.17")
while True:
    frame = remote_cam.get()
    # do stuff
```