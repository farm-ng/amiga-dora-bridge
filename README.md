# amiga-dora-bridge

A [Dora](https://github.com/dora-rs/dora) bridge for the [Farm-ng Amiga](https://farm-ng.com/) robot platform, enabling seamless integration of Amiga sensors and systems with Dora's dataflow framework.

## 🚀 Overview

The `amiga-dora-bridge` provides a comprehensive bridge between the Farm-ng Amiga robot and Dora's dataflow framework, allowing you to:

- **Stream camera feeds** from dual OAK-D cameras
- **Access GPS/GNSS data** for positioning and navigation
- **Read IMU data** for orientation and motion sensing
- **Interface with CAN bus** for vehicle control and telemetry
- **Build real-time dataflows** with Dora's high-performance runtime

## 📦 Components

### Sensor Bridges
- **🎥 Camera Bridge** (`dora-amiga-camera`) - Streams RGB video from OAK-D cameras
- **📍 GPS Bridge** (`dora-amiga-gps`) - Provides GNSS positioning data
- **🧭 IMU Bridge** (`dora-amiga-imu`) - Streams gyroscope and accelerometer data
- **🚗 CAN Bus Bridge** (`dora-amiga-canbus`) - Interfaces with vehicle control system

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- Farm-ng Amiga V6 robot
- Dora-cli runtime environment

### Install from Source
```bash
git clone https://github.com/farm-ng/amiga-dora-bridge.git
cd amiga-dora-bridge
```

### Install the dora-cli runtime

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/dora-rs/dora/releases/latest/download/dora-cli-installer.sh | sh
```

**See https://dora-rs.ai/docs/guides/Installation/installing for more details.**

## 🔧 Configuration

Customize the dataflow.yaml file to include the bridges you want to use
with the `nodes` section.

Explore the dora nodes-hub to start using the latest great AI models.

**See https://dora-rs.ai/docs/nodes/ for more details.**

## 🚀 Quick Start

Start your data pipeline with:

```bash
dora run examples/dataflow.yaml --uv
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

