import click
from ovos_config import Configuration
from ovos_utils import wait_for_exit_signal
from ovos_utils.fakebus import FakeBus

from ovos_PHAL_rediscamera import PHALRedisCamera


@click.command()
@click.option('--camera-id', type=str, help='Name of the device running the camera.')
@click.option('--camera-index', default=0, type=int, help='Index of the camera to be used.')
def standalone_launch(camera_id, camera_index):
    conf = Configuration().get("PHAL", {}).get("ovos-PHAL-rediscamera", {})
    conf.update({"camera_index": camera_index, "device_name": camera_id})
    s = PHALRedisCamera(bus=FakeBus(), config=conf)
    wait_for_exit_signal()
    s.shutdown()


if __name__ == "__main__":
    standalone_launch()
