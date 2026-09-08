import collections
import math
import time
import board
from adafruit_icm20x import ICM20948
from gpiozero import LED

#LED pins
PIN_NORTH_LED = 17  #red LED
PIN_LEVEL_LED = 27  #blue LED

#offsets gotten using mag_offset.py
MAG_OFFSET_X = -9.45
MAG_OFFSET_Y = 19.27

# change this value so 0 degree is north. 
NORTH_ALIGNMENT_OFFSET = 109.0

# Reykjavik offset: -10.5 degrees (west), don't change this.
DECLINATION_DEG = -10.5

TARGET_HEADING_DEG = 0.0     # 0° = North, 90° = East, 180° = South, 270° = West
TARGET_TOLERANCE_DEG = 15.0  # tolerance on "North"

# these are tolerances for determining if the device is level (not tilted)
TILT_TOLERANCE_MS2 = 1.5
GRAVITY_NOMINAL = 9.81

## class for the IMU. 
class IMUController:
    """Class to manage the ICM20948 IMU sensor, compute heading, and check level and target alignment."""
    def __init__(self,):
        self.i2c = board.I2C()

        try:
            self.sensor = ICM20948(self.i2c, address=0x68)
        except (ValueError, OSError):
            self.sensor = ICM20948(self.i2c, address=0x69)

        self.target_heading = TARGET_HEADING_DEG
        self.tolerance = TARGET_TOLERANCE_DEG
        self.accel = (0.0, 0.0, GRAVITY_NOMINAL)
        self.mag = (0.0, 0.0, 0.0)

    #Tries reading the sensor(acc or mag) 3 times. Can change the try values.
    def _safe_fetch(self, attr, retries=3):
        """Attempts to fetch a sensor attribute (like acceleration or magnetic) safely, retrying on OSError."""
        for attempt in range(retries):
            try:
                return getattr(self.sensor, attr)
            except OSError:
                if attempt == retries - 1:
                    return None
                time.sleep(0.01)

    def update(self):
        """Fetches the latest accelerometer and magnetometer readings from the sensor."""
        new_accel = self._safe_fetch("acceleration")
        new_mag = self._safe_fetch("magnetic")

        if new_accel is None or new_mag is None:
            return False

        self.accel = new_accel
        self.mag = new_mag
        return True

    def compute_heading(self):
            """Computes the heading in degrees from the magnetometer readings, applying offsets and declination."""
            mx, my, _ = self.mag
            
            #apply offsets
            cx = mx - MAG_OFFSET_X
            cy = my - MAG_OFFSET_Y

            raw_heading = math.degrees(math.atan2(cy, cx))
            if raw_heading < 0:
                raw_heading += 360.0

            # align physical sensor front with 0° and apply declination
            heading = (raw_heading - NORTH_ALIGNMENT_OFFSET + DECLINATION_DEG) % 360.0

            return heading

    def is_level(self):
        """Checks if the device is level (not tilted) within tolerance."""
        ax, ay, az = self.accel
        xy_flat = abs(ax) < TILT_TOLERANCE_MS2 and abs(ay) < TILT_TOLERANCE_MS2
        z_up = abs(abs(az) - GRAVITY_NOMINAL) < TILT_TOLERANCE_MS2
        return xy_flat and z_up

    def is_facing_target(self):
        """Checks if current heading matches target_heading within tolerance,

        properly handling the 0/360 boundary wrap.
        """
        heading = self.compute_heading()
        diff = abs(heading - self.target_heading) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff
        return diff <= self.tolerance


def main():
    """Main loop to monitor IMU readings and control LEDs based on level and target alignment."""
    red_led = LED(PIN_NORTH_LED)
    blue_led = LED(PIN_LEVEL_LED)
    
    imu = IMUController()
    
    history = collections.deque(maxlen=5)
    print("IMU Active")

    try:
        # main loop
        while True:
            if not imu.update():
                time.sleep(0.05)
                continue

            level = imu.is_level()
            on_target = imu.is_facing_target()
            heading = imu.compute_heading()
            ax, ay, az = imu.accel

            blue_led.value = level
            red_led.value = on_target
            
            timestamp = time.strftime("%H:%M:%S")
            entry = (
                f"[{timestamp}] heading: {heading:5.1f}° | "
                f"target Match: {str(on_target):5} | level: {str(level):5} | "
                f"Z: {az:4.1f} m/s²"
            )
            history.append(entry)

            print("\033[H\033[J", end="")
            print(f"=== Target: {imu.target_heading:.1f}° (±{imu.tolerance:.1f}°) ===")
            for log in history:
                print(log)

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        red_led.off()
        blue_led.off()


if __name__ == "__main__":
    main()
