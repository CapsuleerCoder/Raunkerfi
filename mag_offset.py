import time
import board
from adafruit_icm20x import ICM20948

i2c = board.I2C()
try:
    icm = ICM20948(i2c, address=0x68)
except (ValueError, OSError):
    icm = ICM20948(i2c, address=0x69)

print("rotate the sensor 360 degrees on a flat table for 10seconds")
min_x, max_x = 1000.0, -1000.0
min_y, max_y = 1000.0, -1000.0

start = time.time()
while time.time() - start < 10:
    try:
        mx, my, _ = icm.magnetic
        min_x, max_x = min(min_x, mx), max(max_x, mx)
        min_y, max_y = min(min_y, my), max(max_y, my)
    except OSError:
        pass
    time.sleep(0.05)

off_x = (max_x + min_x) / 2
off_y = (max_y + min_y) / 2

print(f"MAG_OFFSET_X = {off_x:.2f}")
print(f"MAG_OFFSET_Y = {off_y:.2f}")
