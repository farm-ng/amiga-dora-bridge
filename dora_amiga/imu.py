"""Dora bridge for the Farm-ng Amiga IMU."""

from pathlib import Path
import asyncio

from dora import Node
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.events_file_reader import proto_from_json_file
import pyarrow as pa

async def run_imu_bridge() -> None:
    """Main function for the Amiga IMU bridge."""
    service_config_path = Path(__file__).parent / "service_config.json"

    # Load the service config
    config_list: EventServiceConfigList = proto_from_json_file(service_config_path, EventServiceConfigList())

    configs = {}
    for config in config_list.configs:
        configs[config.name] = config

    # Create a client to the camera service
    client_oak0 = EventClient(configs["oak0"])
    client_oak1 = EventClient(configs["oak1"])

    # Subscribe to the camera service streams
    subscription_oak0_imu = client_oak0.subscribe(configs["oak0"].subscriptions[1], decode=True)
    subscription_oak1_imu = client_oak1.subscribe(configs["oak1"].subscriptions[1], decode=True)

    # Create a Dora node and send the IMU data to the next node
    node = Node()

    for event in node:
        if event["type"] == "INPUT":
            if event["id"] == "tick":
                # decode and send the image from the first camera
                event, message = await anext(subscription_oak0_imu)
                print(message)


def main() -> None:
    """Main function for the Amiga IMU bridge."""
    asyncio.run(run_imu_bridge())

if __name__ == "__main__":
    main()