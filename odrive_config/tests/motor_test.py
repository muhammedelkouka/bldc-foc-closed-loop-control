#!/usr/bin/env python3
"""
Orchestrates running specific motor tests and generating csv files.

@author: Austin Owens
@date: 5/4/2024
"""

import argparse
import csv
import signal
import time
from types import FrameType
from typing import Optional

import odrive
from odrive.enums import (AXIS_STATE_CLOSED_LOOP_CONTROL, AXIS_STATE_IDLE,
                          CONTROL_MODE_POSITION_CONTROL,
                          CONTROL_MODE_VELOCITY_CONTROL)

KILL_TEST = False


def signal_handler(sig: int, frame: Optional[FrameType]) -> None:
    """Gracefully handle SIGINT (Ctrl+C) signal."""
    global KILL_TEST

    print("\nStopping motor test...")
    KILL_TEST = True


signal.signal(signal.SIGINT, signal_handler)


class MotorTest:
    """A class to represent a motor test setup."""

    # Max rotations per second
    MAX_VELOCITY_RPS = 1

    def __init__(self, axis_num: int, sample_rate_hz: float, output_file: str):
        """Construct all necessary attributes for running any motor test."""
        self.axis_num = axis_num
        self.sample_rate_hz = sample_rate_hz
        self.output_file = output_file

        # connect to Odrive
        odrv = odrive.find_any()
        self.odrv_axis = getattr(odrv, "axis{}".format(self.axis_num))

        # Set motor in known good state
        input(
            f"Motor at {self.odrv_axis.encoder.pos_estimate}, going to move motor "
            "to 0 degrees. Please enter to start..."
        )
        self.odrv_axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.odrv_axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
        self.odrv_axis.controller.input_pos = 0
        time.sleep(3)

    def _cleanup(self) -> None:
        print("Stopping test...")
        time.sleep(1)
        self.odrv_axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
        self.odrv_axis.controller.input_pos = 0
        time.sleep(3)
        self.odrv_axis.requested_state = AXIS_STATE_IDLE
        print("CSV file located at {}.csv".format(self.output_file))

    def _run_test(self, header: list[str], args: argparse.Namespace) -> None:
        with open(self.output_file + ".csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)

            start_time = time.time()
            sample_time = time.time()

            # Position test setup
            move_time = time.time()
            toggle_pos = 0

            # Velocity test setup
            if args.motor_test == "velocity":
                self.odrv_axis.controller.config.control_mode = (
                    CONTROL_MODE_VELOCITY_CONTROL
                )
                self.odrv_axis.controller.input_vel = args.speed_rps

            while time.time() - start_time <= args.duration:

                if args.motor_test == "position":
                    # Move the motor by 1 rotation every "args.pause_interval" seconds
                    if time.time() - move_time >= args.pause_interval:
                        toggle_pos = not toggle_pos
                        self.odrv_axis.controller.input_pos = toggle_pos
                        move_time = time.time()

                elif args.motor_test == "velocity":
                    pass

                elif args.motor_test == "pid":
                    pass

                # Sample data at "args.sample_rate_hz"
                if time.time() - sample_time >= 1 / args.sample_rate_hz:
                    data = [time.time() - start_time]
                    data += [
                        getattr(self.odrv_axis.encoder, label) for label in header[1:]
                    ]

                    writer.writerow(data)

                    # Print data
                    for label, value in zip(header, data):
                        print(f"{label}: {value}")
                    print()

                    sample_time = time.time()

                if KILL_TEST:
                    self.odrv_axis.requested_state = AXIS_STATE_IDLE
                    break

            self._cleanup()

    def position_test(self, args: argparse.Namespace) -> None:
        """Set motor to position mode and rotate between 0 and 360 degrees."""
        header = [
            "Time",
            "pos_abs",
            "pos_circular",
            "pos_cpr_counts",
            "pos_estimate",
            "pos_estimate_counts",
            "count_in_cpr",
            "vel_estimate",
            "vel_estimate_counts",
        ]

        self._run_test(header, args)

    def velocity_test(self, args: argparse.Namespace) -> None:
        """Set motor to velocity mode and travel at specific RPM."""
        header = [
            "Time",
            "pos_abs",
            "pos_circular",
            "pos_cpr_counts",
            "pos_estimate",
            "pos_estimate_counts",
            "count_in_cpr",
            "vel_estimate",
            "vel_estimate_counts",
        ]

        self._run_test(header, args)

    def pid_test(self, args: argparse.Namespace) -> None:
        """Sweeps across PID values while performing the position test."""
        results = {
            "test": "pid",
            "axis": self.axis_num,
        }
        print(f"PID test results: {results}")


def main() -> None:
    """Parse user arguments and kick off the motor test."""
    parser = argparse.ArgumentParser(description="Motor test script")

    parser.add_argument(
        "--axis_num",
        type=int,
        choices=[0, 1],
        required=True,
        help="Motor axis number (0 or 1).",
    )
    parser.add_argument(
        "--sample_rate_hz",
        type=int,
        required=True,
        help="Sample rate to fetch data from ODrive (in Hz).",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Output file name for the CSV results.",
    )

    subparsers = parser.add_subparsers(dest="motor_test", required=True)

    # Position test
    position_parser = subparsers.add_parser(
        "position", help="Run position control test"
    )
    position_parser.add_argument(
        "pause_interval",
        type=int,
        choices=range(1, 11),
        help="Pause interval (seconds) before moving to the next position after "
        "reaching the target (1-10 seconds).",
    )
    position_parser.add_argument(
        "duration", type=int, help="Total duration (seconds) of the position test."
    )

    # Velocity test
    velocity_parser = subparsers.add_parser(
        "velocity", help="Run velocity control test"
    )
    velocity_parser.add_argument(
        "speed_rps",
        type=float,
        choices=[x / 100 for x in range((MotorTest.MAX_VELOCITY_RPS * 100) + 1)],
        help="Motor speed in revolutions per second (RPS). Max RPS is {}".format(
            MotorTest.MAX_VELOCITY_RPS
        ),
    )
    velocity_parser.add_argument(
        "duration", type=int, help="Total duration (seconds) of the velocity test."
    )

    # PID test
    pid_parser = subparsers.add_parser("pid", help="Run PID control test")

    args = parser.parse_args()

    # Create the MotorTest instance with parsed arguments
    motor_test = MotorTest(args.axis_num, args.sample_rate_hz, args.output_file)

    # Assign the bound methods as defaults
    position_parser.set_defaults(func=motor_test.position_test)
    velocity_parser.set_defaults(func=motor_test.velocity_test)
    pid_parser.set_defaults(func=motor_test.pid_test)

    # Re-parse the arguments to apply the updated defaults
    args = parser.parse_args()

    # Execute the selected function
    args.func(args)


if __name__ == "__main__":
    main()
