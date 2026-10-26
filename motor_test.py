from gpiozero import Motor
from time import sleep

# motor B on J7 -> left motor
motor_left = Motor(forward=18, backward=19, pwm=True)

# motor A on J4 -> right motor
motor_right = Motor(forward=12, backward=13, pwm=True)

print("motor B (left)")
motor_left.forward(0.5)
sleep(1.5)
motor_left.stop()
sleep(0.5)

print("testing motor A (right")
motor_right.forward(0.5)
sleep(1.5)
motor_right.stop()
sleep(0.5)

print("both motors forward")
motor_left.forward(0.5)
motor_right.forward(0.5)
sleep(2)

print("both motors backward")
motor_left.backward(0.5)
motor_right.backward(0.5)
sleep(2)

motor_left.stop()
motor_right.stop()
