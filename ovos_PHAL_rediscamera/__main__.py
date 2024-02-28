from ovos_config import Configuration
from ovos_utils import wait_for_exit_signal

from ovos_utils.fakebus import FakeBus
from ovos_PHAL_rediscamera import PHALRedisCamera


def standalone_launch(conf = None):
    conf = conf or Configuration().get("PHAL", {}).get("ovos-PHAL-rediscamera", {})
    s = PHALRedisCamera(bus=FakeBus(), config=conf)

    wait_for_exit_signal()
    print("Redis server needs to be running")


if __name__ == "__main__":
    # TODO kwargs
    conf = {
        "camera_index": 0,
        "name": "laptop",
        "host": "192.168.1.17",
        "serve_mjpeg": True
    }
    standalone_launch(conf)
