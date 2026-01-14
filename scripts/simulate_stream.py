import time, random, requests
from datetime import datetime

API = "http://127.0.0.1:8000/ingest"

SENSORS = ["HX-001", "HX-002", "T-ROOM-01", "T-ROOM-02", "EXT-01"]

def generate_reading():
    sensor = random.choice(SENSORS)
    temp = round(random.uniform(18, 95), 2)       # 18..95 C
    hum  = round(random.uniform(20, 98), 2)       # 20..98 %
    status = "ok"
    # simple status logic
    if temp > 85:
        status = random.choice(["warn", "fail"])
    return {
        "sensor_id": sensor,
        "ts": datetime.now().isoformat(),
        "temperature_c": temp,
        "humidity_pct": hum,
        "status": status,
    }

def main():
    for i in range(25):
        payload = generate_reading()
        try:
            r = requests.post(API, json=payload, timeout=5)
            if r.status_code == 201:
                print("OK:", r.json())
            else:
                print("ERR:", r.status_code, r.text)
        except Exception as e:
            print("POST failed:", e)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
