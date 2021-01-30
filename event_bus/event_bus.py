import asyncio
import zmq
from zmq.asyncio import Context

ctx = Context.instance()

port_in = "5555"
port_out = "5556"

async def main():
    socket_in = ctx.socket(zmq.SUB)
    socket_out = ctx.socket(zmq.PUB)
    socket_in.bind("tcp://*:%s" % port_in)
    socket_out.bind("tcp://*:%s" % port_out)
    socket_in.setsockopt(zmq.SUBSCRIBE, b"")

    while True:
        msg = await socket_in.recv()
        print('transports')
        print(msg)
        # topic, messagedata = msg.split()
        await socket_out.send(msg)


asyncio.run(main())
