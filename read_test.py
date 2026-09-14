import time
from gpiozero import MCP3008


number = MCP3008(channel=0)
V_REF = 3.3

print("Reading SensoR")

try:
    while True:
        raw = round(number.value * 1023)
        volts = number.value * V_REF
        print(f"{raw:<20} | {volts:.3f} V")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("done")


import threading

def calculate_distance(v):
    return 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 301.439

def distance_monitor():
    while True:
        v = number.value * V_REF
        dist = calculate_distance(v)
        print(f"                                   --> Distanz: {dist:.2f} cm")
        time.sleep(0.5)

dist_thread = threading.Thread(target=distance_monitor, daemon=True)
dist_thread.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("stopping")