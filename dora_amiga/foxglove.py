"""Dora Node for Amiga Foxglove."""

from pathlib import Path

from dora import Node
import foxglove
from foxglove.channels import RawImageChannel, Vector3Channel
from foxglove.schemas import RawImage, LocationFix, Vector3, Timestamp
import pyarrow as pa

def timestamp_from_seconds(seconds: float) -> Timestamp:
    return Timestamp(
        sec=int(seconds),
        nsec=int((seconds - int(seconds)) * 1e9)
    )

def main() -> None:
    node = Node()

    foxglove.start_server(
        name="amiga_foxglove",
        port=8080,
        host="0.0.0.0",
    )

    img_chan_oak0_rgb = RawImageChannel(topic="oak0/rgb")
    img_chan_oak1_rgb = RawImageChannel(topic="oak1/rgb")
    twist_chan = Vector3Channel(topic="twist")
    imu_chan_oak0_gyro = Vector3Channel(topic="oak0/imu/gyro")
    imu_chan_oak0_accel = Vector3Channel(topic="oak0/imu/accel")
    imu_chan_oak1_gyro = Vector3Channel(topic="oak1/imu/gyro")
    imu_chan_oak1_accel = Vector3Channel(topic="oak1/imu/accel")

    for event in node:
        if event["type"] == "INPUT":
            if "rgb" in event["id"]:
                storage = event["value"]
                metadata = event["metadata"]

                device, _ = event["id"].split("/")

                raw_image = RawImage(
                    timestamp=timestamp_from_seconds(metadata["timestamp"]),
                    frame_id=device,
                    data=storage.to_numpy().tobytes(),
                    step=metadata["width"] * 3,
                    width=metadata["width"],
                    height=metadata["height"],
                    encoding="rgb8",
                )

                match device:
                    case "oak0":
                        img_chan_oak0_rgb.log(raw_image)
                    case "oak1":
                        img_chan_oak1_rgb.log(raw_image)
                    case _:
                        raise ValueError(f"Unknown device: {device}")
            
            if "imu" in event["id"]:
                storage = event["value"].to_pylist()

                # convert timestamp from seconds to nanoseconds
                stamp_ns = int(storage[0] * 1e9)
                vec = Vector3(
                    x=storage[1],
                    y=storage[2],
                    z=storage[3],
                )

                device, _, mode = event["id"].split("/")

                match device:
                    case "oak0":
                        match mode:
                            case "gyro":
                                imu_chan_oak0_gyro.log(
                                    vec,
                                    log_time=stamp_ns,
                                )
                            case "accel":
                                imu_chan_oak0_accel.log(
                                    vec,
                                    log_time=stamp_ns,
                                )
                            case _:
                                raise ValueError(f"Unknown mode: {mode}")
                    case "oak1":
                        match mode:
                            case "gyro":
                                imu_chan_oak1_gyro.log(
                                    vec,
                                    log_time=stamp_ns,
                                )
                            case "accel":
                                imu_chan_oak1_accel.log(
                                    vec,
                                    log_time=stamp_ns,
                                )
                            case _:
                                raise ValueError(f"Unknown mode: {mode}")
                    case _:
                        raise ValueError(f"Unknown device: {device}")   
            
            if event["id"] == "twist":
                storage = event["value"].to_pylist()

                # convert timestamp from seconds to nanoseconds
                stamp_ns = int(storage[0] * 1e9)

                twist_chan.log(
                    Vector3(
                        x=storage[1],
                        y=storage[2],
                        z=storage[3],
                    ),
                    log_time=stamp_ns,
                )

if __name__ == "__main__":
    main()