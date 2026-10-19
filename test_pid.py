import time
from gpiozero import RotaryEncoder, DigitalOutputDevice, Motor
from simple_pid import PID
import robot_config as cfg


slp = DigitalOutputDevice(cfg.PIN_SLP, initial_value=True)
left_enc = RotaryEncoder(cfg.PIN_ENC_LEFT_A, cfg.PIN_ENC_LEFT_B, max_steps=0)
right_enc = RotaryEncoder(cfg.PIN_ENC_RIGHT_A, cfg.PIN_ENC_RIGHT_B, max_steps=0)
left_motor = Motor(cfg.PIN_MOTOR_LEFT_FWD, cfg.PIN_MOTOR_LEFT_BWD, pwm=True)
right_motor = Motor(cfg.PIN_MOTOR_RIGHT_FWD, cfg.PIN_MOTOR_RIGHT_BWD, pwm=True)

TARGET_SPEED = 1500.0  
SAMPLE_TIME = 0.05  #50 ms 

# Note: output_limits=(0.0, 1.0) for gpiozero Motor
pid_left = PID(
    Kp=0.0003, Ki=0.0008, Kd=0.00001,
    setpoint=TARGET_SPEED,
    sample_time=SAMPLE_TIME,
    output_limits=(0.0, 1.0)
)

pid_right = PID(
    Kp=0.0003, Ki=0.0008, Kd=0.00001,
    setpoint=TARGET_SPEED,
    sample_time=SAMPLE_TIME,
    output_limits=(0.0, 1.0)
)

last_left_steps = 0
last_right_steps = 0
last_time = time.time()

print(f"Goal speed: {TARGET_SPEED}")

try:
    while True:
        time.sleep(SAMPLE_TIME)

        now = time.time()
        dt = now - last_time
        last_time = now

        # Read encoder ticks
        current_left = left_enc.steps
        current_right = right_enc.steps

        # ticks / sec
        speed_left = (current_left - last_left_steps) / dt
        speed_right = (current_right - last_right_steps) / dt

        last_left_steps = current_left
        last_right_steps = current_right

        # PWM duty cycle [0.0 - 1.0] from simple pid
        pwm_left = pid_left(speed_left)
        pwm_right = pid_right(speed_right)

        # Apply to motors
        left_motor.forward(pwm_left)
        right_motor.forward(pwm_right)

        print(
            f"Left: {speed_left:6.1f} (PWM: {pwm_left:.2f}) | "
            f"R: {speed_right:6.1f} (PWM: {pwm_right:.2f}) | "
            f"Goal: {TARGET_SPEED:.0f}"
        )

except KeyboardInterrupt:
    left_motor.stop()
    right_motor.stop()
    slp.off()