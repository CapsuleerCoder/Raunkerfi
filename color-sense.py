import time
import board
import busio
import adafruit_ssd1306
import adafruit_tcs34725

#IC2 set up
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tcs34725.TCS34725(i2c)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

while True:
    #read values
    r, g, b = sensor.color_rgb_bytes
    r_raw, g_raw, b_raw, clear = sensor.color_raw

    # print to command
    print(f"RGB: ({r}, {g}, {b}) | Raw Clear: {clear}")

    # print to oled screen.
    oled.fill(0)
    oled.text("TESTING SAMPLES", 0, 0, 1)
    oled.text(f"R: {r}", 0, 18, 1)
    oled.text(f"G: {g}", 0, 30, 1)
    oled.text(f"B: {b}", 0, 42, 1)
    oled.text(f"Clear: {clear}", 0, 54, 1)
    oled.show()

    time.sleep(1)