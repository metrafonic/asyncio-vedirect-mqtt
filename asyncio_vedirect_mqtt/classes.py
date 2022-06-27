import asyncio
from asyncio_mqtt import Client
import ssl
import json


class AsyncVeDirectMqtt():
    def __init__(self, tty, name, broker, *args, tls_protocol=None, port=1883, username=None, password=None, verbose=False, timeout=60,
                 ca_path=None, **kwargs):
        self.tty = tty
        self.name = name
        self.broker = broker
        self.port = int(port)
        self.username = username
        self.password = password
        self.verbose = verbose
        self.timeout = timeout
        self.ssl_context = ssl.SSLContext(tls_protocol) if tls_protocol else None
        if ca_path and self.ssl_context:
            self.ssl_context.load_verify_locations(capath=ca_path)

    async def run(self):
        async with Client(hostname=self.broker, port=self.port, tls_context=self.ssl_context, username=self.username,
                          password=self.password) as client:
            await client.publish("test/test", payload=json.dumps({1: 23}), qos=2, retain=False)
