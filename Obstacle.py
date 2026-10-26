import time
import math
import board
import busio
import adafruit_icm20x
from gpiozero import RotaryEncoder, DigitalOutputDevice, Motor, MCP3008
from simple_pid import PID
import robot_config as cfg

slp = DigitalOutputDevice(cfg.PIN_SLP, initial_value=True)

left_enc = RotaryEncoder(cfg.PIN_ENC_LEFT_A, cfg.PIN_ENC_LEFT_B, max_steps=0)
right_enc = RotaryEncoder(cfg.PIN_ENC_RIGHT_A, cfg.PIN_ENC_RIGHT_B, max_steps=0)

left_motor = Motor(cfg.PIN_MOTOR_LEFT_FWD, cfg.PIN_MOTOR_LEFT_BWD, pwm=True)
right_motor = Motor(cfg.PIN_MOTOR_RIGHT_FWD, cfg.PIN_MOTOR_RIGHT_BWD, pwm=True)

adc_ir = MCP3008(channel=cfg.ADC_CH_IR_DISTANCE, device=0)

i2c = busio.I2C(board.SCL, board.SDA)
imu = adafruit_icm20x.ICM20948(i2c, address=cfg.I2C_ADDR_IMU)

FORWARD_SPEED = 1400.0
SAMPLE_TIME = 0.05
DISTANCE_THRESHOLD = 25.0

pid_left = PID(
    Kp=0.0003, Ki=0.0008, Kd=0.00001,
    setpoint=FORWARD_SPEED,
    sample_time=SAMPLE_TIME,
    output_limits=(0.0, 1.0)
)
pid_right = PID(
    Kp=0.0003, Ki=0.0008, Kd=0.00001,
    setpoint=FORWARD_SPEED,
    sample_time=SAMPLE_TIME,
    output_limits=(0.0, 1.0)
)

def get_distance():
    """MCP3008 CH0 and converts voltage to distance in cm"""
    voltage = adc_ir.value * 3.3
    if voltage > 0.4:
        return 27.86 / (voltage - 0.1)
    return 999.0

def get_gyro_z_bias(samples=20):
    """measures zero-motion offset on the Z-gyro axis while stationary"""
    bias = 0.0
    for _ in range(samples):
        _, _, gz = imu.gyro
        bias += gz
        time.sleep(0.01)
    return bias / samples

def turn_right_degrees(target_deg=90.0):
    """spins right in place until integrated gyro yaw reaches target_deg"""
    print(f"\n[AVOID] Obstacle ahead! Executing {target_deg}° gyro-guided turn...")
    left_motor.stop()
    right_motor.stop()
    time.sleep(0.15)

    z_bias = get_gyro_z_bias()

    current_angle = 0.0
    last_turn_time = time.time()

    left_motor.forward(0.35)
    right_motor.backward(0.35)

    while abs(current_angle) < target_deg:
        now = time.time()
        dt = now - last_turn_time
        last_turn_time = now

        _, _, gz = imu.gyro
        rate_rad = gz - z_bias
        rate_deg = math.degrees(rate_rad)

        current_angle += rate_deg * dt
        time.sleep(0.01)

    left_motor.stop()
    right_motor.stop()
    time.sleep(0.2)

    pid_left.reset()
    pid_right.reset()
    print(f"[AVOID] Turn finished at {abs(current_angle):.1f}°. Path clear, resuming.\n")

last_left = left_enc.steps
last_right = right_enc.steps
last_time = time.time()

print("Obstacle Avoidance System Active (IR + PID + IMU). Driving forward...")

try:
    while True:
        time.sleep(SAMPLE_TIME)

        now = time.time()
        dt = now - last_time
        last_time = now

        dist = get_distance()

        # Obstacle check
        if dist <= DISTANCE_THRESHOLD:
            turn_right_degrees(90.0)
            last_left = left_enc.steps
            last_right = right_enc.steps
            last_time = time.time()
            continue

        # Normal forward PID drive
        cur_left = left_enc.steps
        cur_right = right_enc.steps

        speed_left = (cur_left - last_left) / dt
        speed_right = (cur_right - last_right) / dt

        last_left = cur_left
        last_right = cur_right

        pwm_left = pid_left(speed_left)
        pwm_right = pid_right(speed_right)

        left_motor.forward(pwm_left)
        right_motor.forward(pwm_right)

        print(
            f"Dist: {dist:4.1f}cm | "
            f"L: {speed_left:5.0f} (PWM {pwm_left:.2f}) | "
            f"R: {speed_right:5.0f} (PWM {pwm_right:.2f})"
        )

except KeyboardInterrupt:
    left_motor.stop()
    right_motor.stop()
    slp.off()
    print("\nRover halted.")