# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html
# https://learnopencv.com/read-write-and-display-a-video-using-opencv-cpp-python/


import zmq
import random
import sys
import time
import xdrlib
import numpy as np

DTYPES = {
    'int64': 1,
    'float64': 2
}


port = "5555"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
# socket.bind("tcp://*:%s" % port)
socket.connect("tcp://localhost:%s" % port)
data_packer = xdrlib.Packer()

while True:
    topic = random.randrange(9999,10005)
    data_array = np.random.rand(3,2)
    data_packer.pack_uint(topic)
    data_packer.pack_array(data_array.shape, data_packer.pack_uint)
    data_packer.pack_uint(DTYPES[data_array.dtype.name])
    data_packer.pack_bytes(data_array.tobytes())
    print('sending')
    print(topic)
    print(data_array)
    socket.send(data_packer.get_buffer())
    data_packer.reset()
    # time.sleep(1)
