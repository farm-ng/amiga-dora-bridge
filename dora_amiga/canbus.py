"""Dora bridge for the Farm-ng Amiga cameras."""

from pathlib import Path
import asyncio

from dora import Node
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.events_file_reader import proto_from_json_file
import pyarrow as pa


async def run_gps_bridge() -> None:
    """Main function for the Amiga GPS bridge."""
    service_config_path = Path(__file__).parent / "service_config.json"

    # Load the service config
    config_list: EventServiceConfigList = proto_from_json_file(service_config_path, EventServiceConfigList())

    configs = {}
    for config in config_list.configs:
        configs[config.name] = config

    # Create a client to the camera service
    client = EventClient(configs["canbus"])

    # Subscribe to the camera service
    subscriptions = client.subscribe(configs["canbus"].subscriptions[0], decode=True)

    # Create a Dora nodesend the image to the next node
    node = Node()

    for event in node:
        if event["type"] == "INPUT":
            if event["id"] == "tick":
                # decode and send the image from the first camera
                event, message = await anext(subscriptions)

                # get the timestamp when the message was received by the driver
                timestamp = event.timestamps[0]
                assert timestamp.semantics == "driver/receive"

                # send the twist2d message
                node.send_output(
                    "twist",
                    pa.array([message.linear_velocity_x, message.linear_velocity_y, message.angular_velocity]),
                    metadata={
                        "schema": "Twist2d:vx,vy,w",
                        "stamp": timestamp.stamp,
                    }
                )

def main() -> None:
    """Main function for the Amiga GPS bridge."""
    asyncio.run(run_gps_bridge())

if __name__ == "__main__":
    main()