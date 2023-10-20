import re
import logging
import json
from asyncio_mqtt import Client

logger = logging.getLogger(__name__)


class Device(dict):
    def __init__(self, name, model, manufacturer, sw_version='1.0', device_id=None):
        super().__init__()
        self.device_id = re.sub('[^0-9a-zA-Z]+', '_', device_id if device_id else name).lower()
        self.name = name
        self['name'] = name
        self['sw_version'] = sw_version
        self['model'] = model
        self['manufacturer'] = manufacturer
        self['identifiers'] = self.device_id


class Sensor:
    def __init__(self, mqtt_client: Client, name, category, parent_device: Device, unit_of_measurement: str = None, device_class: str = None, state_class: str = None, discovery_prefix='homeassistant', sensor_id=None, multiplier: float=None, mov_avg: int=None):
        self.sensor_id = re.sub('[^0-9a-zA-Z]+', '_', sensor_id if sensor_id else name).lower()
        self.parent_device = parent_device
        self.mqtt_client = mqtt_client
        self.multiplier = multiplier
        self.mov_avg = mov_avg
        self.discovery_topic = f"{discovery_prefix}/sensor/{parent_device.device_id}/{self.sensor_id}/config"
        self.state_topic =f"{parent_device.device_id}/sensor/{category}/{self.sensor_id}/state"
        self.discovery_attributes = {
            "schema": "json",
            'platform': 'mqtt',
            'name': f"{self.parent_device.name} {name}",
            'state_topic': self.state_topic,
            'device': dict(self.parent_device),
            'unique_id': f"{self.parent_device.device_id}_{self.sensor_id}"
        }
        if unit_of_measurement:
            self.discovery_attributes['unit_of_measurement'] = unit_of_measurement
        if device_class:
            self.discovery_attributes['device_class'] = device_class
        if state_class:
            self.discovery_attributes['state_class'] = state_class
        self.last_n = []

    async def publish_discovery(self):
       logger.debug(f"Publishing discovery to {self.discovery_topic}")
       await self.mqtt_client.publish(self.discovery_topic, payload=json.dumps(self.discovery_attributes), qos=0, retain=True)


    async def send(self, value):
        if self.multiplier:
            value = round(float(value) * self.multiplier, 2)
        if self.mov_avg:
            self.last_n.append(float(value))
            value = round(float(round(sum(self.last_n), 2) / len(self.last_n)), 2)
            if len(self.last_n) > self.mov_avg:
                self.last_n = []
            else:
                return
        logger.debug(f"Publishing data to {self.state_topic}: {value=}")
        await self.mqtt_client.publish(self.state_topic, payload=value)