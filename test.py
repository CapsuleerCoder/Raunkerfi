import time
import board
import busio
import adafruit_tcs34725
from gpiozero import RotaryEncoder, DigitalOutputDevice, Motor
import robot_config as cfg

slp = DigitalOutputDevice(cfg.PIN_SLP, initial_value=True)

left_enc = RotaryEncoder(cfg.PIN_ENC_LEFT_A, cfg.PIN_ENC_LEFT_B, max_steps=0)
right_enc = RotaryEncoder(cfg.PIN_ENC_RIGHT_A, cfg.PIN_ENC_RIGHT_B, max_steps=0)

left_motor = Motor(cfg.PIN_MOTOR_LEFT_FWD, cfg.PIN_MOTOR_LEFT_BWD, pwm=True)
right_motor = Motor(cfg.PIN_MOTOR_RIGHT_FWD, cfg.PIN_MOTOR_RIGHT_BWD, pwm=True)

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50  # 50 ms
sensor.gain = 4


THRESHOLD = 4870.0
TICKS_PER_TURN = 4  
STEP_PWM = 0.2

def step_left_wheel(ticks):
    start = left_enc.steps
    left_motor.forward(STEP_PWM)
    right_motor.stop()
    
    while abs(left_enc.steps - start) < ticks:
        time.sleep(0.002)
        
    left_motor.stop()

def step_right_wheel(ticks):
    start = right_enc.steps
    left_motor.stop()
    right_motor.forward(STEP_PWM)
    
    while abs(right_enc.steps - start) < ticks:
        time.sleep(0.002)
        
    right_motor.stop()

def stop_all():
    left_motor.stop()
    right_motor.stop()


try:
    while True:

        raw_clear = sensor.color_raw[3]

        if raw_clear < THRESHOLD:
            step_left_wheel(TICKS_PER_TURN)
            action = "ON TAPE  -> Step Right"
        else:
            step_right_wheel(TICKS_PER_TURN)
            action = "ON FLOOR -> Step Left "

        print(f"Clear: {raw_clear:5d} | {action} ")
        
        time.sleep(0.02)

except KeyboardInterrupt:
    stop_all()
    slp.off()
