# Import required Python libraries
import argparse
import logging
import sys
import time
import xdrlib

logger = logging.getLogger(__name__)

import zmq
from gpiozero import DistanceSensor


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

    logger.info(f"Ultrasonic Measurement. Setting up GPIO: trigger at {trigger_pin} and echo at {echo_pin}...")

    distance_sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin, queue_len=2)

    # Allow module to settle
    time.sleep(sensor_settle_time)

    try:
        while True:
            distance = distance_sensor.distance * 100
            logger.debug(f"Ultrasonic Measurement - Distance: {distance} cm")

            # Send event if measured distance is less than set threshold
            if distance <= threshold_distance:
                data_packer.pack_uint(topic)
                data_packer.pack_float(distance)
                socket.send(data_packer.get_buffer())
                data_packer.reset()

            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.warning("End by user keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(1)


if __name__ == '__main__':
    # Run module
    main()
