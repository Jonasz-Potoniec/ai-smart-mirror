# Import required Python libraries
import argparse
import logging
import sys
import time
import xdrlib
from threading import Thread, Event

logger = logging.getLogger(__name__)

import RPi.GPIO as GPIO
import zmq



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

def main():
    # Creates Argument Parser object named parser
    parser = argparse.ArgumentParser()

    # Set arguments
    parser.add_argument('--event_bus_server', default="127.0.0.1",)
    parser.add_argument('--trig', type=int, default=16, help='PIN with TRIGGER output PIN.')
    parser.add_argument('--echo', type=int, default=18, help='PIN with ECHO input PIN.')
    parser.add_argument('--sleep', type=float, default=0.1, help='Sleep time between distance measurements.')
    parser.add_argument('--port_out', default="5555", help='Port to which connect to')
    parser.add_argument('--topic_out', type=int, default=10001, help='Event bus topic for the distance sensor')
    parser.add_argument('--thresholddistance', type=int, default=80, help='Threshold distance under which sensor '
                                                                          'will fire an event.')
    parser.add_argument('--sensorsettletime', type=float, default=0.3, help='Time for the sensor to settle after '
                                                                            'setting the Trigger pin to the LOW state')
    parser.add_argument('--log_level', default="WARNING", help='Sets log level - what messages are logger.infoed out')

    # Get command line arguments
    init_args = parser.parse_args()
    trigger_pin = init_args.trig
    echo_pin = init_args.echo
    sleep_time = init_args.sleep
    port = init_args.port_out
    topic = init_args.topic_out
    event_bus_server = init_args.event_bus_server
    threshold_distance = init_args.thresholddistance
    sensor_settle_time = init_args.sensorsettletime
    log_level = init_args.log_level

    publish_url = f"tcp://{event_bus_server}:{port}"
    logging.basicConfig(level=log_level.upper())
    logger.info(f'sensor ready, producing events to : {topic} on {publish_url}')

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(publish_url)
    data_packer = xdrlib.Packer()

    logger.info("Ultrasonic Measurement. Setting up GPIO...")

    distance_sensor = DistanceSensor(trigger_pin, echo_pin)

    # Allow module to settle
    time.sleep(sensor_settle_time)

    event = Event()
    t = Thread(target=distance_sensor.watch, args=(sleep_time, event))
    t.start()
    try:
        while True:
            logger.debug(f"Ultrasonic Measurement - Distance: {distance_sensor.distance} cm")
            # Send event if measured distance is less than set threshold
            if distance_sensor.distance <= threshold_distance:
                data_packer.pack_uint(topic)
                data_packer.pack_float(distance_sensor.distance)
                socket.send(data_packer.get_buffer())
                data_packer.reset()

            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.warning("End by user keyboard interrupt")
        event.set()
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(1)
    finally:
        t.join()
        GPIO.cleanup()


if __name__ == '__main__':
    # Run module
    main()
