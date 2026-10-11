"""
Robot Pinout Configuration
The formatting will be as follows

# Part
USE = GPIO number # PI PIN > other side PIN

"""

# DRV8833
PIN_SLP = 17  # Pi Pin 11 -> J12 SLP

# MOTOR B
PIN_MOTOR_LEFT_FWD = 19   # Pi Pin 35 -> MOTB Pin 1
PIN_MOTOR_LEFT_BWD = 18   # Pi Pin 12 -> MOTB Pin 2
PIN_ENC_LEFT_A = 20       # Pi Pin 38 -> MOTB Pin 3 
PIN_ENC_LEFT_B = 21       # Pi Pin 40 -> MOTB Pin 4 


# MOTOR A

PIN_MOTOR_RIGHT_FWD = 13  # Pi Pin 33 -> MOTA Pin 1
PIN_MOTOR_RIGHT_BWD = 12  # Pi Pin 32 -> MOTA Pin 2
PIN_ENC_RIGHT_A = 5       # Pi Pin 29 -> MOTA Pin 3 
PIN_ENC_RIGHT_B = 6       # Pi Pin 31 -> MOTA Pin 4 

