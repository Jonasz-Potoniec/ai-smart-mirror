import logging
import sys
import time
from threading import Thread, Event

logger = logging.getLogger(__name__)

import RPi.GPIO as GPIO


class DistanceSensor:
    # Consts that don't need to be set from the outside
    SPEED_OF_SOUND = 34300  # cm/s
    HALF_SPEED_OF_SOUND = SPEED_OF_SOUND / 2
    TRIGGER_PULSE_TIME = 0.00001  # Needs to be 10us pulse to trigger the sensor

    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.echo_start = 0
        self.echo_stop = 0
        self.distance = -1

        # GPIO.BOARD map PIN numbers like on BOARD.
        # GPIO.BCM map PIN numbers like in documentation.
        GPIO.setmode(GPIO.BOARD)  # Setting PIN numbers context.
        GPIO.setwarnings(False)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

        # Set trigger to False (Low)
        GPIO.output(self.trigger_pin, False)
        GPIO.add_event_detect(self.echo_pin, GPIO.BOTH, callback=self.handle_echo_pin_change)

    def send_trigger(self):
        """ Send trigger pulse to fire up measurement process """
        # Send pulse to trigger
        GPIO.output(self.trigger_pin, True)
        time.sleep(self.TRIGGER_PULSE_TIME)
        GPIO.output(self.trigger_pin, False)

    def handle_echo_pin_change(self, channel):
        """ Handle changes for the pin (high and low voltage)
            Parameters:
                channel (int): A pin number to listen changes on
        """
        # Check if the pin is in High or Low state
        if GPIO.input(channel):
            self.echo_start = time.time()
            self.echo_stop = self.echo_start
            # do not reset distance to let other thread to read it
        else:
            self.echo_stop = time.time()
            # Calculate pulse length
            pulse_duration = self.echo_stop - self.echo_start
            self.distance = round(pulse_duration * self.HALF_SPEED_OF_SOUND, 2)

    def watch(self, sleep_time, event):
        while True:
            if event.is_set():
                break
            self.send_trigger()
            time.sleep(sleep_time)


def start_measuring_distance(distance: int):
    # Get command line arguments
    trigger_pin = 16
    echo_pin = 18
    sleep_time = 0.1
    threshold_distance = 80
    sensor_settle_time = 0.3
    log_level = "WARNING"

    logging.basicConfig(level=log_level.upper())

    print("DUPA")

    logger.info("Ultrasonic Measurement. Setting up GPIO...")

    distance_sensor = DistanceSensor(trigger_pin, echo_pin)

    event = Event()
    t = Thread(target=distance_sensor.watch, args=(sleep_time, event))
    t.start()

    # Allow module to settle
    time.sleep(sensor_settle_time)
    try:
        while True:
            logger.debug(f"Ultrasonic Measurement - Distance: {distance_sensor.distance} cm")
            # Send event if measured distance is less than set threshold
            if distance_sensor.distance <= threshold_distance:
                distance = distance_sensor.distance
                logger.info(f'Camera send signal to ECU.')
                time.sleep(3)  # To not spam camera with requests we waiting with some time

            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.warning("End by user keyboard interrupt.")
        event.set()
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(1)
    finally:
        t.join()
        GPIO.cleanup()
