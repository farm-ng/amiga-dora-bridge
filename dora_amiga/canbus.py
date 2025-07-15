"""Dora bridge for the Farm-ng Amiga cameras."""

from pathlib import Path
import asyncio

from dora import Node
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.events_file_reader import proto_from_json_file
import pyarrow as pa

canbus_schema = pa.schema([
    ("timestamp_device", pa.timestamp("ns")),
    ("linear_velocity_x", pa.float64()),
    ("linear_velocity_y", pa.float64()),
    ("angular_velocity", pa.float64()),
])


async def run_canbus_bridge() -> None:
    """Main function for the Amiga CANbus bridge."""
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
                try:
                    event, message = await asyncio.wait_for(
                        anext(subscriptions), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    continue

                # get the timestamp when the message was received by the driver
                timestamp = event.timestamps[0]
                assert timestamp.semantics == "driver/receive"

                # send the twist2d message
                node.send_output(
                    "twist",
                    pa.array([timestamp.stamp, message.linear_velocity_x, message.linear_velocity_y, message.angular_velocity]),
                    metadata={
                        "schema": canbus_schema.to_string(),
                        "content_type": "canbus/twist",
                    }
                )

def main() -> None:
    """Main function for the Amiga CANbus bridge."""
    asyncio.run(run_canbus_bridge())

if __name__ == "__main__":
    main()