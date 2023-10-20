import aioserial
from vedirect import Vedirect as VedirectSync
import logging

logger = logging.getLogger(__name__)


class AsyncIOVeDirect(VedirectSync):
    def __init__(self, serialport, timeout, *args, **kwargs):
        super(AsyncIOVeDirect, self).__init__(serialport, timeout)
        self.ser = aioserial.AioSerial(port=serialport, timeout=timeout, baudrate=19200)

    async def read_data_single(self):
        while True:
            data = await self.ser.read_async()
            for single_byte in data:
                packet = self.input(single_byte)
                if (packet != None):
                    return packet

    async def read_data_callback(self, callbackFunction):
        while True:
            data = await self.ser.read_async()
            for byte in data:
                packet = self.input(byte)
                if (packet != None):
                    await callbackFunction(packet)