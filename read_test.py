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
        
        # 4th-order polynomial calibration for distance (cm)
        dist = 16.2537 * volts**4 - 129.893 * volts**3 + 382.268 * volts**2 - 512.611 * volts + 301.439
        
        print(f"{raw:<10} | {volts:.3f} V | Distanz: {dist:.2f} cm")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("done")

