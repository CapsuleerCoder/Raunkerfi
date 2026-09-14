import time
from gpiozero import MCP3008


number = MCP3008(channel=0)
V_REF = 3.3

print("Reading SensoR")

try:
    while True:
        # adc.value returns a normalized float from 0.0 to 1.0
        raw = round(number.value * 1023)
        volts = number.value * V_REF
        print(f"{raw:<20} | {volts:.3f} V")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("done")
