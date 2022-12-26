import asyncio
from asyncio_mqtt import Client, MqttError
import ssl
import json
from asyncio_vedirect_mqtt.victron import AsyncIOVeDirect
from asyncio_vedirect_mqtt.hass_discovery import Sensor, Device
import logging
import time

logger = logging.getLogger(__name__)

class AsyncIOVeDirectMqtt:
    def __init__(self, tty, device, broker, *args, tls_protocol=None, port=1883, username=None, password=None, verbose=False, timeout=60,
                 ca_path=None, **kwargs):
        self.tty = tty
        self.device_name = device
        self.broker = broker
        self.port = int(port)
        self.username = username
        self.password = password
        self.verbose = verbose
        self.mqtt_exception = None
        self.ve_connection = AsyncIOVeDirect(tty, timeout)
        self.ssl_context = ssl.SSLContext(tls_protocol) if tls_protocol else None
        if ca_path and self.ssl_context:
            self.ssl_context.load_verify_locations(capath=ca_path)
        self.sensor_mapping = {}

    async def setup_sensors(self, mqtt_client):
        logger.info("Publishing sensors to home assistant")
        device = Device(self.device_name, 'SmartSolar 75/10', 'Victron')
        self.sensor_mapping["H19"] = Sensor(
            mqtt_client,
            "Yield Total",
            category="Solar",
            parent_device=device,
            unit_of_measurement="kWh",
            device_class="energy",
            state_class="total_increasing",
            multiplier=0.01,
            mov_avg=60
        )
        self.sensor_mapping["H20"] = Sensor(
            mqtt_client,
            "Yield Today",
            category="Solar",
            parent_device=device,
            unit_of_measurement="kWh",
            device_class="energy",
            state_class="total_increasing",
            multiplier=0.01,
            mov_avg=60
        )
        self.sensor_mapping["V"] = Sensor(
            mqtt_client,
            "Battery Voltage",
            category="Solar",
            parent_device=device,
            unit_of_measurement="V",
            device_class="voltage",
            state_class="measurement",
            multiplier=0.001,
            mov_avg=60
        )
        self.sensor_mapping["VPV"] = Sensor(
            mqtt_client,
            "Panel Voltage",
            category="Solar",
            parent_device=device,
            unit_of_measurement="V",
            device_class="voltage",
            state_class="measurement",
            multiplier=0.001,
            mov_avg=60
        )
        self.sensor_mapping["I"] = Sensor(
            mqtt_client,
            "Battery Current",
            category="Solar",
            parent_device=device,
            unit_of_measurement="A",
            device_class="current",
            state_class="measurement",
            multiplier=0.001,
            mov_avg=60
        )
        self.sensor_mapping["IL"] = Sensor(
            mqtt_client,
            "Load Current",
            category="Solar",
            parent_device=device,
            unit_of_measurement="A",
            device_class="current",
            state_class="measurement",
            multiplier=0.001,
            mov_avg=60
        )
        self.sensor_mapping["PPV"] = Sensor(
            mqtt_client,
            "Panel Power",
            category="Solar",
            parent_device=device,
            unit_of_measurement="W",
            device_class="power",
            state_class="measurement",
            mov_avg=60
        )
        for key in self.sensor_mapping.keys():
            await self.sensor_mapping[key].publish_discovery()


    async def publish_data(self, data):
        for key, value in data.items():
            if key in self.sensor_mapping.keys():
                try:
                    await self.sensor_mapping[key].send(value)
                except MqttError:
                    self.mqtt_exception = MqttError

    async def run(self):
        reconnect_interval = 5  # In seconds
        while True:
            try:
                logger.info(f"Initiating connection to broker ({self.broker}:{self.port} {self.ssl_context=})")
                async with Client(hostname=self.broker, port=self.port, tls_context=self.ssl_context, username=self.username,
                                  password=self.password) as client:
                    logger.info("Connection to broker successful")
                    await self.setup_sensors(client)
                    logger.info(f"Listening for ve.direct data on {self.tty}")
                    while True:
                        if self.mqtt_exception:
                            raise self.mqtt_exception
                        ve_data = await self.ve_connection.read_data_single()
                        asyncio.create_task(self.publish_data(ve_data), name='publish_data')
            except MqttError as error:
                self.mqtt_exception = None
                logger.error(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
                await asyncio.sleep(reconnect_interval)
