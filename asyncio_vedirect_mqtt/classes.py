import asyncio
from asyncio_mqtt import Client
import ssl
import json
import aioserial
from vedirect import Vedirect as VedirectSync
import logging
import time

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


class AsyncIOVeDirectMqtt:
    def __init__(self, tty, topic, broker, *args, tls_protocol=None, port=1883, username=None, password=None, verbose=False, timeout=60,
                 ca_path=None, **kwargs):
        self.tty = tty
        self.topic = topic
        self.broker = broker
        self.port = int(port)
        self.username = username
        self.password = password
        self.verbose = verbose
        self.ve_connection = AsyncIOVeDirect(tty, timeout)
        self.ssl_context = ssl.SSLContext(tls_protocol) if tls_protocol else None
        if ca_path and self.ssl_context:
            self.ssl_context.load_verify_locations(capath=ca_path)

    async def publish_data(self, client, data):
        logger.debug('Publishing to MQTT server')
        start_time = time.monotonic_ns()
        await client.publish(self.topic, payload=json.dumps(data), qos=2, retain=False)
        logger.debug(f'Publish took {time.monotonic_ns() - start_time}ns')


    async def run(self):
        logger.info(f"Connecting to {self.broker}:{self.port}")
        async with Client(hostname=self.broker, port=self.port, tls_context=self.ssl_context, username=self.username,
                          password=self.password) as client:
            logger.info(f"Listening for data on {self.tty}")
            while True:
                ve_data = await self.ve_connection.read_data_single()
                asyncio.create_task(self.publish_data(client, ve_data))
                logger.debug(ve_data)
