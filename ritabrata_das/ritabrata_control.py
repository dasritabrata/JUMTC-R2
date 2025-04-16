

# ritabrata_control.py
import asyncio
import websockets
import json
import re
import random
import math

SERVER_URI = "ws://localhost:8765"
INITIAL_SPEED = 5
INITIAL_ALTITUDE = 170   
CONTROL_INTERVAL = 0.15  
MAX_X_RANGE = 100000
SAFE_ALTITUDE_GREEN = 20  
SAFE_ALTITUDE_YELLOW = 250  
CRITICAL_LOW_BATTERY = 15  
STABILIZATION_THRESHOLD = 3  
MIN_SAFE_BATTERY_FOR_ASCEND = 40
OPTIMAL_GREEN_ALTITUDE = 120
OPTIMAL_YELLOW_ALTITUDE = 200
WIND_IMPACT_THRESHOLD = 50
DUST_IMPACT_THRESHOLD = 50

async def control_drone():
    try:
        async with websockets.connect(SERVER_URI) as websocket:
            print("Connected to the drone simulator.")
            speed = INITIAL_SPEED
            altitude = INITIAL_ALTITUDE
            movement = "fwd"
            last_movement_change = 0
            stuck_count = 0
            previous_x = 0
            total_distance = 0

            while True:
                command = {
                    "speed": int(speed),
                    "altitude": int(altitude),
                    "movement": movement
                }
                await websocket.send(json.dumps(command))
                print(f"Sent command: {command}")

                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.4)
                    print(f"Received response: {response}")
                    telemetry_data = parse_telemetry(response)

                    if telemetry_data["status"] == "crashed":
                        print(f"Drone crashed! Total distance: {total_distance:.2f}")
                        break

                    current_x = telemetry_data["telemetry"].get("x_position", 0)
                    total_distance += abs(current_x - previous_x)
                    previous_x = current_x

                    speed, altitude, movement, last_movement_change, stuck_count, previous_x = make_decision(
                        telemetry_data,
                        speed,
                        altitude,
                        movement,
                        last_movement_change,
                        stuck_count,
                        previous_x
                    )

                    battery = telemetry_data["telemetry"].get("battery", 100)
                    if battery <= 1:
                        print(f"Battery depleted. Total distance: {total_distance:.2f}")
                        break

                except asyncio.TimeoutError:
                    print("No response from server.")
                except websockets.ConnectionClosedOK:
                    print(f"Connection closed by the server. Total distance: {total_distance:.2f}")
                    break
                except websockets.ConnectionClosedError as e:
                    print(f"Connection closed unexpectedly: {e}. Total distance: {total_distance:.2f}")
                    break

                await asyncio.sleep(CONTROL_INTERVAL)

    except ConnectionRefusedError:
        print("Server connection refused. Make sure the server is running.")
    except Exception as e:
        print(f"An error occurred: {e}")

def parse_telemetry(response_str):
    data = {"status": None, "telemetry": {}, "metrics": {}}
    if "{" in response_str:
        try:
            json_part = response_str[response_str.find("{"):]
            json_data = json.loads(json_part)
            data["status"] = json_data.get("status")
            data["metrics"] = json_data.get("metrics", {})
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    telemetry_match = re.search(r"X-(\d+)-Y-([+-]?\d+)-BAT-(\d+)-GYR-\[([\d.-]+),([\d.-]+),([\d.-]+)\]-WIND-(\d+)-DUST-(\d+)-SENS-(\w+)", response_str)
    if telemetry_match:
        data["telemetry"] = {
            "x_position": int(telemetry_match.group(1)),
            "y_position": int(telemetry_match.group(2)),
            "battery": int(telemetry_match.group(3)),
            "gyroscope": [float(g) for g in telemetry_match.group(4, 5, 6)],
            "wind_speed": int(telemetry_match.group(7)),
            "dust_level": int(telemetry_match.group(8)),
            "sensor_status": telemetry_match.group(9)
        }
    return data

def make_decision(telemetry_data, current_speed, current_altitude, current_movement, last_movement_change, stuck_count, previous_x):
    speed = current_speed
    altitude = current_altitude
    movement = current_movement
    battery = telemetry_data["telemetry"].get("battery", 100)
    x_position = telemetry_data["telemetry"].get("x_position", 0)
    y_position = telemetry_data["telemetry"].get("y_position", 0)
    sensor_status = telemetry_data["telemetry"].get("sensor_status", "GREEN")
    wind_speed = telemetry_data["telemetry"].get("wind_speed", 0)
    dust_level = telemetry_data["telemetry"].get("dust_level", 0)
    gyroscope = telemetry_data["telemetry"].get("gyroscope", [0, 0, 0])
    iterations = telemetry_data["metrics"].get("iterations", 0)

    
    if battery <= CRITICAL_LOW_BATTERY:
        speed = max(1, speed - 2) 
        altitude = max(10, altitude - 15) 
    elif y_position < 0:
        altitude = max(10, altitude + 25) 
    elif sensor_status == "RED":
        altitude = max(5, altitude - 40) 

    
    elif sensor_status == "GREEN":
        if altitude < OPTIMAL_GREEN_ALTITUDE and battery > MIN_SAFE_BATTERY_FOR_ASCEND:
            altitude += 8
        elif altitude > OPTIMAL_GREEN_ALTITUDE + 20:
            altitude -= 7
    elif sensor_status == "YELLOW":
        if altitude < OPTIMAL_YELLOW_ALTITUDE and battery > MIN_SAFE_BATTERY_FOR_ASCEND:
            altitude += 5
        elif altitude > OPTIMAL_YELLOW_ALTITUDE + 30:
            altitude -= 10
        elif y_position < SAFE_ALTITUDE_YELLOW * 0.5:
            altitude += 10 

  
    if wind_speed > WIND_IMPACT_THRESHOLD or dust_level > DUST_IMPACT_THRESHOLD:
        speed = max(1, speed - 1) 
    elif speed < INITIAL_SPEED and battery > CRITICAL_LOW_BATTERY:
        speed = min(INITIAL_SPEED, speed + 1)

  
    if abs(gyroscope[1]) > STABILIZATION_THRESHOLD or abs(gyroscope[2]) > STABILIZATION_THRESHOLD:
        speed = max(0, speed - 2) 

    
    if abs(x_position) > MAX_X_RANGE * 0.8:
        if (x_position > 0 and movement == "fwd") or (x_position < 0 and movement == "rev"):
            movement = "rev" if movement == "fwd" else "fwd"
            speed = INITIAL_SPEED
            last_movement_change = iterations
            stuck_count = 0

   
    if x_position == previous_x and speed > 0:
        stuck_count += 1
        if stuck_count > 15 and (iterations - last_movement_change) > 25:
            movement = random.choice(["fwd", "rev"])
            speed = INITIAL_SPEED
            altitude += random.randint(-10, 15) 
            last_movement_change = iterations
            stuck_count = 0
    else:
        stuck_count = 0

    return speed, altitude, movement, last_movement_change, stuck_count, previous_x

if __name__ == "__main__":
    asyncio.run(control_drone())