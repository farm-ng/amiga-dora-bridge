"""Dora bridge for the Farm-ng Amiga cameras."""

from pathlib import Path
import asyncio

from dora import Node
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.events_file_reader import proto_from_json_file

import cv2
import numpy as np
import pyarrow as pa

async def next_event_and_decode(subscription):
    """Get the next event from the subscription and decode the image."""
    # await the next event containing the image
    _, message = await anext(subscription)
    # TODO: implement with kornia_rs
    image_bgr8 = cv2.imdecode(np.frombuffer(message.image_data, dtype="uint8"), cv2.IMREAD_UNCHANGED)
    image_rgb8 = cv2.cvtColor(image_bgr8, cv2.COLOR_BGR2RGB)
    return message, image_rgb8


async def run_camera_bridge() -> None:
    """Main function for the Amiga camera bridge."""
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
    subscription_oak0 = client_oak0.subscribe(configs["oak0"].subscriptions[0], decode=True)
    subscription_oak1 = client_oak1.subscribe(configs["oak1"].subscriptions[0], decode=True)

    # Create a Dora nodesend the image to the next node
    node = Node()

    for event in node:
        if event["type"] == "INPUT":
            if event["id"] == "tick":
                # decode and send the image from the first camera
                try:
                    message, image_rgb8 = await asyncio.wait_for(
                        next_event_and_decode(subscription_oak0), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    continue

                # send the message to the next node
                node.send_output(
                    "oak0/rgb",
                    pa.array(image_rgb8.ravel()),
                    metadata={
                        "encoding": "rgb8",
                        "width": image_rgb8.shape[1],
                        "height": image_rgb8.shape[0],
                        "sequence_num": message.meta.sequence_num,
                        "timestamp": message.meta.timestamp,
                    }
                )

                # decode and send the image from the second camera
                try:
                    message, image_rgb8 = await asyncio.wait_for(
                        next_event_and_decode(subscription_oak1), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    continue

                # send the message to the next node
                node.send_output(
                    "oak1/rgb",
                    pa.array(image_rgb8.ravel()),
                    metadata={
                        "encoding": "rgb8",
                        "width": image_rgb8.shape[1],
                        "height": image_rgb8.shape[0],
                        "sequence_num": message.meta.sequence_num,
                        "timestamp": message.meta.timestamp,
                    }
                )

def main() -> None:
    """Main function for the Amiga camera bridge."""
    asyncio.run(run_camera_bridge())

if __name__ == "__main__":
    main()