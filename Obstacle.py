import time
import board
import busio
from gpiozero import RotaryEncoder, DigitalOutputDevice, Motor, MCP3008
from simple_pid import PID
import robot_config as cfg
from monster import Monster

# 1. Hardware Pin & Device Initialization
slp = DigitalOutputDevice(cfg.PIN_SLP, initial_value=True)

left_enc = RotaryEncoder(cfg.PIN_ENC_LEFT_A, cfg.PIN_ENC_LEFT_B, max_steps=0)
right_enc = RotaryEncoder(cfg.PIN_ENC_RIGHT_A, cfg.PIN_ENC_RIGHT_B, max_steps=0)

left_motor = Motor(cfg.PIN_MOTOR_LEFT_FWD, cfg.PIN_MOTOR_LEFT_BWD, pwm=True)
right_motor = Motor(cfg.PIN_MOTOR_RIGHT_FWD, cfg.PIN_MOTOR_RIGHT_BWD, pwm=True)

adc_ir = MCP3008(channel=cfg.ADC_CH_IR_DISTANCE, device=0)

# Initialize I2C and Monster Face
i2c = busio.I2C(board.SCL, board.SDA)
monster = Monster(i2c=i2c)
monster.set_mood("normal")

# 2. Control Parameters
FORWARD_SPEED = 700.0   # Test and video speed
SAMPLE_TIME = 0.05
DISTANCE_THRESHOLD = 25.0
TICKS_FOR_90_DEG = 190
REVERSE_TICKS = 350

LEFT_STALL_PWM = 0.35
RIGHT_STALL_PWM = 0.35
STALL_CYCLES_REQUIRED = 5

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
    print("\n[OBSTACLE] Executing 90° turn...")
    monster.set_mood("scared")  # Reacts to turning away from danger
    
    left_motor.stop()
    right_motor.stop()
    time.sleep(0.15)

    start_left = left_enc.steps
    start_right = right_enc.steps

    left_motor.forward(0.35)
    right_motor.backward(0.35)

    t0 = time.time()
    while True:
        delta_left = abs(left_enc.steps - start_left)
        delta_right = abs(right_enc.steps - start_right)
        avg_ticks = (delta_left + delta_right) / 2.0

        if avg_ticks >= TICKS_FOR_90_DEG or (time.time() - t0 > 2.0):
            break
        time.sleep(0.01)

    left_motor.stop()
    right_motor.stop()
    time.sleep(0.15)

    pid_left.reset()
    pid_right.reset()
    print("[TURN] Done. Resuming forward\n")

def reverse_backoff(ticks=REVERSE_TICKS):
    print(f"\n[WALL DETECTED] Reversing {ticks} ticks")
    monster.set_mood("laughing")  # Cheeky face when escaping a physical collision
    
    left_motor.stop()
    right_motor.stop()
    time.sleep(0.1)

    start_left = left_enc.steps
    start_right = right_enc.steps

    left_motor.backward(0.30)
    right_motor.backward(0.30)

    t0 = time.time()
    while True:
        delta_left = abs(left_enc.steps - start_left)
        delta_right = abs(right_enc.steps - start_right)
        avg_ticks = (delta_left + delta_right) / 2.0

        if avg_ticks >= ticks or (time.time() - t0 > 3.0):
            break
        time.sleep(0.01)

    left_motor.stop()
    right_motor.stop()
    time.sleep(0.15)

    pid_left.reset()
    pid_right.reset()
    print("[WALL CLEARED]")

last_left = left_enc.steps
last_right = right_enc.steps
last_time = time.time()
stall_counter = 0

print("collision avoidance ongoing, also stall detection")
monster.set_mood("grin")

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
            stall_counter = 0
            continue

        cur_left = left_enc.steps
        cur_right = right_enc.steps

        speed_left = (cur_left - last_left) / dt
        speed_right = (cur_right - last_right) / dt

        last_left = cur_left
        last_right = cur_right

        pwm_left = pid_left(speed_left)
        pwm_right = pid_right(speed_right)

        if (pwm_left >= LEFT_STALL_PWM) or (pwm_right >= RIGHT_STALL_PWM):
            stall_counter += 1
        else:
            stall_counter = 0

        if stall_counter >= STALL_CYCLES_REQUIRED:
            reverse_backoff(REVERSE_TICKS)
            turn_right_encoder_90()
            last_left = left_enc.steps
            last_right = right_enc.steps
            last_time = time.time()
            stall_counter = 0
            continue

        monster.set_mood("grin")
        left_motor.forward(pwm_left)
        right_motor.forward(pwm_right)

        print(
            f"Dist: {dist:4.1f}cm | "
            f"L_PWM: {pwm_left:.2f} (>{LEFT_STALL_PWM}) | "
            f"R_PWM: {pwm_right:.2f} (>{RIGHT_STALL_PWM}) | "
            f"Stall Count: {stall_counter}",
            end="\r"
        )

except KeyboardInterrupt:
    left_motor.stop()
    right_motor.stop()
    slp.off()
    monster.clear()
    print("\nProgram stopped.")