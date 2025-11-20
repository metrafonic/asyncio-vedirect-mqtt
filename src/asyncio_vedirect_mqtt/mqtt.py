import asyncio
from asyncio_mqtt import Client, MqttError
import ssl
from asyncio_vedirect_mqtt.victron import AsyncIOVeDirect
from asyncio_vedirect_mqtt.hass_discovery import Sensor, Device
import logging

logger = logging.getLogger(__name__)

device_types = {
    "mppt": {
        "model": "BlueSolar 100/50",
        "category": "Solar",
        "sensors": {
            "H19": {
                "name": "Yield Total",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "multiplier": 0.01,
            },
            "H20": {
                "name": "Yield Today",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "multiplier": 0.01,
            },
            "V": {
                "name": "Output Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "VPV": {
                "name": "Panel Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "I": {
                "name": "Output Current",
                "unit_of_measurement": "A",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            # "IL": {
            #     "name": "Load Current",
            #     "unit_of_measurement": "A",
            #     "device_class": "current",
            #     "state_class": "measurement",
            #     "multiplier": 0.001
            # },
            "PPV": {
                "name": "Panel Power",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "multiplier": 1,
            },
        },
    },
    "shunt": {
        "model": "SmartShunt 500A/50mV",
        "category": "Battery",
        "sensors": {
            "V": {
                "name": "Battery Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "VS": {
                "name": "Vehicle Battery Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "I": {
                "name": "Battery Current",
                "unit_of_measurement": "A",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "P": {
                "name": "Battery Power",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "CE": {
                "name": "Consumed Ah",
                "unit_of_measurement": "Ah",
                "device_class": "current",
                "state_class": "total_increasing",
                "multiplier": 0.001,
            },
            "SOC": {
                "name": "Battery Percentage",
                "unit_of_measurement": "%",
                "device_class": "battery",
                "state_class": "measurement",
                "multiplier": 0.1,
            },
            "TTG": {
                "name": "Time Remaining",
                "unit_of_measurement": "min",
                "device_class": "duration",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "Alarm": {
                "name": "Alarm",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": None,
            },
            "AR": {
                "name": "Alarm Reason",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": None,
            },
            "H1": {
                "name": "Depth of Deepest Discharge",
                "unit_of_measurement": "Ah",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "H2": {
                "name": "Depth of Last Discharge",
                "unit_of_measurement": "Ah",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "H3": {
                "name": "Depth of Average Discharge",
                "unit_of_measurement": "Ah",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "H4": {
                "name": "Number of Charge Cycles",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "H5": {
                "name": "Number of Full Discharges",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "H6": {
                "name": "Cumulative Ah Drawn",
                "unit_of_measurement": "Ah",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "H7": {
                "name": "Minimum Battery Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "H8": {
                "name": "Maximum Battery Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "H9": {
                "name": "Time Since Last Full Charge",
                "unit_of_measurement": "s",
                "device_class": "duration",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "H10": {
                "name": "Synchronisations",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "H11": {
                "name": "Low Voltage Alarms",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "H12": {
                "name": "High Voltage Alarms",
                "unit_of_measurement": "",
                "device_class": "None",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "H17": {
                "name": "Total Discharged Energy",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "measurement",
                "multiplier": 0.01,
            },
            "H18": {
                "name": "Total Charged Energy",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "measurement",
                "multiplier": 0.01,
            },
        },
    },
    "b2b": {
        "model": "Orion XS 12V | 12V 50A",
        "category": "Charger",
        "sensors": {
            "V": {
                "name": "Battery Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "DC_IN_V": {
                "name": "Starter Battery Voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "multiplier": 0.01,
            },
            "I": {
                "name": "Battery Current",
                "unit_of_measurement": "A",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.001,
            },
            "DC_IN_I": {
                "name": "Starter Battery Current",
                "unit_of_measurement": "A",
                "device_class": "current",
                "state_class": "measurement",
                "multiplier": 0.1,
            },
            "P": {
                "name": "Battery Power",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "multiplier": 1,
            },
            "DC_IN_P": {
                "name": "Starter Battery Power",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "multiplier": 1,
            },
        },
    },
}


class AsyncIOVeDirectMqtt:
    def __init__(
        self,
        tty,
        device,
        type,
        broker,
        *args,
        tls_protocol=None,
        windowing=60,
        port=1883,
        username=None,
        password=None,
        mqttretry=30,
        verbose=False,
        timeout=60,
        ca_path=None,
        **kwargs,
    ):
        self.tty = tty
        self.device_name = device
        self.device_type = device_types[type]
        self.broker = broker
        self.port = int(port)
        self.username = username
        self.password = password
        self.mqttretry = mqttretry
        self.verbose = verbose
        self.windowing = windowing
        self.mqtt_exception = None
        self.ve_connection = AsyncIOVeDirect(tty, timeout)
        self.ssl_context = ssl.SSLContext(tls_protocol) if tls_protocol else None
        if ca_path and self.ssl_context:
            self.ssl_context.load_verify_locations(capath=ca_path)
        self.sensor_mapping = {}

    async def setup_sensors(self, mqtt_client):
        logger.info("Publishing sensors to home assistant")
        device = Device(self.device_name, self.device_type["model"], "Victron")

        for sensor_id in self.device_type["sensors"]:
            sensor = self.device_type["sensors"][sensor_id]
            self.sensor_mapping[sensor_id] = Sensor(
                mqtt_client,
                sensor["name"],
                category=self.device_type["category"],
                parent_device=device,
                unit_of_measurement=sensor["unit_of_measurement"],
                device_class=sensor["device_class"],
                state_class=sensor["state_class"],
                multiplier=sensor["multiplier"],
                mov_avg=None if sensor["multiplier"] == None else self.windowing,
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
        while True:
            try:
                logger.info(
                    f"Initiating connection to broker ({self.broker}:{self.port} {self.ssl_context=})"
                )
                async with Client(
                    hostname=self.broker,
                    port=self.port,
                    tls_context=self.ssl_context,
                    username=self.username,
                    password=self.password,
                ) as client:
                    logger.info("Connection to broker successful")
                    await self.setup_sensors(client)
                    logger.info(f"Listening for ve.direct data on {self.tty}")
                    while True:
                        if self.mqtt_exception:
                            raise self.mqtt_exception
                        ve_data = await self.ve_connection.read_data_single()
                        asyncio.create_task(
                            self.publish_data(ve_data), name="publish_data"
                        )
            except MqttError as error:
                self.mqtt_exception = None
                logger.error(
                    f'Error "{error}". Reconnecting in {self.mqttretry} seconds.'
                )
                await asyncio.sleep(self.mqttretry)
