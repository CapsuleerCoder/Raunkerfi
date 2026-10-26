import time
from gpiozero import RotaryEncoder, DigitalOutputDevice, Motor, MCP3008
from simple_pid import PID
import robot_config as cfg

slp = DigitalOutputDevice(cfg.PIN_SLP, initial_value=True)

left_enc = RotaryEncoder(cfg.PIN_ENC_LEFT_A, cfg.PIN_ENC_LEFT_B, max_steps=0)
right_enc = RotaryEncoder(cfg.PIN_ENC_RIGHT_A, cfg.PIN_ENC_RIGHT_B, max_steps=0)

left_motor = Motor(cfg.PIN_MOTOR_LEFT_FWD, cfg.PIN_MOTOR_LEFT_BWD, pwm=True)
right_motor = Motor(cfg.PIN_MOTOR_RIGHT_FWD, cfg.PIN_MOTOR_RIGHT_BWD, pwm=True)

adc_ir = MCP3008(channel=cfg.ADC_CH_IR_DISTANCE, device=0)

FORWARD_SPEED = 1400.0
SAMPLE_TIME = 0.05
DISTANCE_THRESHOLD = 25.0

TICKS_FOR_90_DEG = 190

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
    """Reads MCP3008 CH0 and converts voltage to distance in cm."""
    voltage = adc_ir.value * 3.3
    if voltage > 0.4:
        return 27.86 / (voltage - 0.1)
    return 999.0

def turn_right_encoder_90():
    """Executes a 90-degree tank turn using encoder counts."""
    print("\n[AVOID] Obstacle ahead! Executing 90° turn via encoders...")
    left_motor.stop()
    right_motor.stop()
    time.sleep(0.15)

    start_left = left_enc.steps
    start_right = right_enc.steps

    left_motor.forward(0.35)
    right_motor.backward(0.35)

    while True:
        delta_left = abs(left_enc.steps - start_left)
        delta_right = abs(right_enc.steps - start_right)
        avg_ticks = (delta_left + delta_right) / 2.0

        if avg_ticks >= TICKS_FOR_90_DEG:
            break
        time.sleep(0.01)

    left_motor.stop()
    right_motor.stop()
    time.sleep(0.15)

    pid_left.reset()
    pid_right.reset()
    print("[AVOID] Turn complete. Resuming forward drive.\n")

last_left = left_enc.steps
last_right = right_enc.steps
last_time = time.time()

print("Obstacle Avoidance Active (IR + PID + Encoders). Driving forward...")

try:
    while True:
        time.sleep(SAMPLE_TIME)

        now = time.time()
        dt = now - last_time
        last_time = now

        dist = get_distance()

        if dist <= DISTANCE_THRESHOLD:
            turn_right_encoder_90()
            last_left = left_enc.steps
            last_right = right_enc.steps
            last_time = time.time()
            continue

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
    print("\nProgram stopped.")