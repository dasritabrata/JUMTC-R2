# Drone Simulator

A WebSocket-based drone simulator that provides real-time telemetry data and simulates environmental conditions affecting drone flight.

## Features

- Real-time drone flight simulation with position tracking
- Battery simulation with realistic drain based on operations
- Environmental condition simulation (wind, dust, sensor status)
- WebSocket server for remote control and monitoring
- Telemetry persistence between sessions
- Crash detection with detailed reporting
- Comprehensive logging system with configurable outputs
- Command-line tools for log analysis and system monitoring

## Project Structure

```
drone_simulator/
├── __init__.py
├── admin_server.py     # Admin monitoring server
├── client.py           # WebSocket client for drone control
├── dashboard.py        # Admin dashboard interface
├── drone.py            # Core drone simulation logic
├── environment.py      # Environmental condition simulator
├── logging_config.py   # Centralized logging configuration
├── main.py             # Simple example usage
├── run_server.py       # Server startup script
├── server.py           # WebSocket server implementation
├── telemetry.py        # Telemetry data management
└── validators.py       # Input validation utilities
your_name/
├── __init__.py
└── your_code.py       # Your work for drone simulator
tools/
└── log_viewer.py       # Utility for viewing and filtering logs
```

## Getting Started

### Prerequisites

- Python 3.7+
- websockets
- pytest (for running tests)
- tabulate (for admin dashboard)
- asyncio
- pygame (for visualization)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

```bash
python drone_simulator/run_server.py
```

The server will start on `ws://localhost:8765` by default.

### Connecting Clients

You can connect to the simulator using:

1. The included client. Run this in a new terminal:
```bash
python drone_simulator/client.py
```

## Admin Dashboard

Monitor all drone connections with the admin dashboard:

```bash
python drone_simulator/dashboard.py
```

## Logging System

The simulator features a comprehensive logging system:

- All components log to both console and files
- Log files are stored in the `logs/` directory
- Different components have separate log files (server.log, client.log, drone.log)
- Logging level is configurable (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Log Viewer Tool

The log viewer tool helps analyze log files:

```bash
python tools/log_viewer.py --file server.log --level WARNING
```

Options:
- `--file`: Specific log file to view
- `--list`: List all available log files
- `--hours`/`--minutes`: Filter logs by time period
- `--level`: Filter by log level
- `--text`: Filter logs containing specific text
- `--tail`: Show only the last N lines

## API Reference

### Client Commands

Send JSON commands to control the drone:

```json
{
    "speed": 0-5,        // Integer speed (0-5)
    "altitude": integer, // Positive or negative integer for altitude change
    "movement": "fwd"|"rev" // Forward or reverse movement
}
```

### Server Responses

The server responds with telemetry data in a text-encoded format.

```json
{
    "status": "success"|"crashed",
    "telemetry": "X-{x_position}-Y-{y_position}-BAT-{battery}-GYR-{gyroscope}-WIND-{wind_speed}-DUST-{dust_level}-SENS-{sensor_status}",
    "metrics": {
        "iterations": integer,
        "total_distance": float
    }
}
```

The text-encoded telemetry format follows this pattern:
```
X-<x_position>-Y-<y_position>-BAT-<battery>-GYR-[<gx>,<gy>,<gz>]-WIND-<wind_speed>-DUST-<dust_level>-SENS-<sensor_status>
```

Clients should decode this format to access telemetry values.

## Crash Conditions

The drone will crash under the following conditions:

- **Battery Depletion**: Battery level reaches 0%
- **Ground Collision**: Altitude (y_position) becomes negative
- **Range Exceeded**: x_position exceeds maximum range (±100,000 units)
- **Unsafe Altitude for Sensor Status**:
  - RED sensor status: Altitude must stay below 3 units
  - YELLOW sensor status: Altitude must stay below 1000 units
- **Excessive Tilt**: Movement-induced tilt exceeds 45 degrees

## Flight Characteristics

- Iterations are only counted when both speed and altitude are non-zero
- Battery drain is affected by altitude, speed, and altitude changes
- Wind and dust levels affect sensor status (GREEN → YELLOW → RED)
- Sensor status determines safe operating altitude limits
- Gyroscope readings indicate drone stability and tilt

### Altitude-Based Battery Drain

- Battery drains faster at low altitudes (up to 1.8x at ground level)
- Battery drains slower at high altitudes (down to 0.6x at very high altitudes)


### Gyroscope Stability

- More stable at higher altitudes, less stable near the ground
- Wind affects tilt but cannot exceed 45 degrees
- Movement can cause tilt beyond 45 degrees, leading to crashes

### Judging Criteria

- Number of Iteration and Distance Covered in a single flight without crashing. The higher the better.

## Your Work

- Create a folder named `your_name` eg: `rohan_das`.
- Inside the folder add your script to simulate the drone.
- You should read the drone output, parse it and send the instructions.
- Your aim is to keep the drone in flight without crashing and traverse the longest distance.
- You are allowed to make changes only to the `your_name` folder.
- You can use anything and everything.
- Best of luck. [PS: Tears contain salt and might short-circuit your computer.]

