import math
import time
import board
import adafruit_icm20x
from gpiozero import LED

#LED bulbs
red_led = LED(17)  
blue_led = LED(27)

i2c = board.I2C()

try:
    icm = adafruit_icm20x.ICM20948(i2c, address=0x69)
except ValueError:
    icm = adafruit_icm20x.ICM20948(i2c, address=0x68)

while True:
    ax, ay, az = icm.acceleration
    mx, my, mz = icm.magnetic

    #BLUE LED /reads accel and shows level if the device is flat and not moving
    if abs(ax) < 1.5 and abs(ay) < 1.5 and abs(abs(az) - 9.8) < 1.5:
        blue_led.on()
    else:
        blue_led.off()

    #calculate heading from magnetometer readings
    heading = math.degrees(math.atan2(my, mx))
    if heading < 0:
        heading += 360

    #RED LED 
    if heading <= 20 or heading >= 340:
        red_led.on()
    else:
        red_led.off()

    print(f"heading: {heading:.1f}° | accel Z: {az:.2f} m/s^2 | mag: ({mx:.1f}, {my:.1f})")
    time.sleep(0.5)# how often it refreshes the readings in console



