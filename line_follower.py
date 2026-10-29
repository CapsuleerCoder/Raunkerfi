import time
import board
import busio
import adafruit_tcs34725
from gpiozero import RotaryEncoder, DigitalOutputDevice, Motor, MCP3008
import robot_config as cfg
from monster import Monster

slp = DigitalOutputDevice(cfg.PIN_SLP, initial_value=True)

left_enc = RotaryEncoder(cfg.PIN_ENC_LEFT_A, cfg.PIN_ENC_LEFT_B, max_steps=0)
right_enc = RotaryEncoder(cfg.PIN_ENC_RIGHT_A, cfg.PIN_ENC_RIGHT_B, max_steps=0)

left_motor = Motor(cfg.PIN_MOTOR_LEFT_FWD, cfg.PIN_MOTOR_LEFT_BWD, pwm=True)
right_motor = Motor(cfg.PIN_MOTOR_RIGHT_FWD, cfg.PIN_MOTOR_RIGHT_BWD, pwm=True)

adc_ir = MCP3008(channel=cfg.ADC_CH_IR_DISTANCE, device=0)
i2c = busio.I2C(board.SCL, board.SDA)

sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50  # 50 ms
sensor.gain = 4

#initialize the monster display and set it
monster = Monster(i2c=i2c)
monster.set_mood("normal")

THRESHOLD = 4870.0
TICKS_PER_TURN = 20  
STEP_PWM = 0.2
DISTANCE_STOP_CM = 24.0

def get_front_distance():
    voltage = adc_ir.value * 3.3
    if voltage > 0.4:
        return 27.86 / (voltage - 0.1)
    return 999.0

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


input(print ("Put car down on on right side of tape, then press enter"))
try:
    while True:
        dist = get_front_distance()
        if dist <= DISTANCE_STOP_CM:
            stop_all()
            monster.set_mood("scared")
            print(f"[OBSTACLE] Distance -{dist:4.1f} cm (Blocked)     ", end="\r")
            time.sleep(0.05)
            continue

        raw_clear = sensor.color_raw[3]
        
        step_left_wheel(TICKS_PER_TURN)
        step_right_wheel(TICKS_PER_TURN)

        if raw_clear < THRESHOLD:
            monster.set_mood("laughing")
            step_left_wheel(TICKS_PER_TURN)
            action = "ON TAPE  -> Step Right"
        else:
            monster.set_mood("normal")
            step_right_wheel(TICKS_PER_TURN)
            action = "ON FLOOR -> Step Left "

        print(f" Clear reading: {raw_clear:5d} | {action} | IR: {dist:4.1f} cm", end="\r")
        time.sleep(0.02)

except KeyboardInterrupt:
    stop_all()
    slp.off()
    monster.clear()
    print("\nProgram stopped.")
