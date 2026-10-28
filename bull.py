#!/usr/bin/env python3
import time
import curses
from gpiozero import DigitalOutputDevice, Motor, Robot

# Wake up DRV8833 (GPIO 17 connected to J12 SLP pin)
slp = DigitalOutputDevice(17, initial_value=True)

# Motors configured with forward-facing polarities
# Left Motor = MOTB (Pins 19, 18)
# Right Motor = MOTA (Pins 13, 12)
robot = Robot(
    left=Motor(forward=19, backward=18, pwm=True),
    right=Motor(forward=13, backward=12, pwm=True)
)

def main(stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)  # Non-blocking getch (-1 when no key pressed)
    curses.noecho()

    stdscr.clear()
    stdscr.addstr(0, 2, "=== Lab 6: Rover Teleoperation ===")
    stdscr.addstr(2, 2, "W: Forward | S: Backward | A: Left | D: Right")
    stdscr.addstr(3, 2, "E / Space: Stop | Q: Quit")
    stdscr.addstr(5, 2, "Status: READY - STOPPED")
    stdscr.refresh()

    current_state = "STOPPED"

    try:
        while True:
            key = stdscr.getch()

            if key != -1:
                if key in (ord('w'), ord('W')):
                    robot.forward(0.2)
                    current_state = "FORWARD  "
                elif key in (ord('s'), ord('S')):
                    robot.backward(0.2)
                    current_state = "BACKWARD "
                elif key in (ord('a'), ord('A')):
                    robot.left(0.2)
                    current_state = "TURN LEFT"
                elif key in (ord('d'), ord('D')):
                    robot.right(0.2)
                    current_state = "TURN RIGHT"
                elif key in (ord('e'), ord('E'), ord(' ')):
                    robot.stop()
                    current_state = "STOPPED  "
                elif key in (ord('q'), ord('Q')):
                    break

                stdscr.addstr(5, 2, f"Status: RUNNING - {current_state}")
                stdscr.refresh()

            time.sleep(0.04)

    finally:
        robot.stop()
        slp.off()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    finally:
        print("\nShutdown complete: motors stopped, driver put to sleep.")