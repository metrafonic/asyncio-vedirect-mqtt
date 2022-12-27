# asyncio-vedirect-mqtt

This is a simple program for publishing serial data from the Victron VE.Direct protocol
to an mqtt broker in an asynchronous manner. 

The data is published according to the [Home Assistant MQTT Discovery specification](https://www.home-assistant.io/docs/mqtt/discovery/). This allows the device to be auto-discovered in home assistant.

Currently the program is set up for use with SmartSolar devices. Adding more devices is possible (pull requests accepted).

This is done using [changyuheng/aioserial](https://github.com/changyuheng/aioserial) to read the serial data and passing it through 
to an async implementation of [karioja/vedirect](https://github.com/karioja/vedirect) to decode the data. This is then sent over MQTT to a 
broker of your choice via [sbtinstruments/asyncio-mqtt](https://github.com/sbtinstruments/asyncio-mqtt).

The implementation supports TLS and authentication when connecting to the MQTT server.

## Getting started:
Install the latest wheel package from the [releases](https://github.com/metrafonic/asyncio-vedirect-mqtt/releases/latest) tab or
download from git with pip.
```commandline
pip3 install git+https://github.com/metrafonic/asyncio-vedirect-mqtt.git
```
NOTE: Installing the pre-build wheel (as opposed to git install via pip) is recommended as it saves a significant amount of space.

This will add the `ve-mqtt` executable to `~/.local/bin`.

### Run the code:
```text
$ ve-mqtt -h
usage: ve-mqtt [-h] --tty TTY --device DEVICE [-v] [--timeout TIMEOUT] --broker BROKER
               [--port PORT] [--username USERNAME] [--password PASSWORD] [--mqttretry MQTTRETRY] [--tls] [--tls1.2]
               [--ca_path CA_PATH]

Async implementation of ve.direct to mqtt

options:
  -h, --help             show this help message and exit
  --tty TTY              Serial port with incoming ve.direct data
  --device DEVICE        Unique name of the device
  -v, --verbose          Run with verbose logging
  --timeout TIMEOUT      Serial port read timeout
  --broker BROKER        MQTT broker hostname
  --port PORT            MQTT broker port
  --username USERNAME    MQTT broker username
  --password PASSWORD    MQTT broker password
  --mqttretry MQTTRETRY  MQTT broker reconnect timeout interval
  --tls                  Use TLS for MQTT communication
  --tls1.2               Use TLS version 1.2 for MQTT communication
  --ca_path CA_PATH      Custom TLS CA path


```

## System service
Add the following to `/lib/systemd/system/ve-mqtt.service`:
Remember to replace the arguments with your own variables
```text
[Unit]
Description=VE.Direct over MQTT
After=multi-user.target

[Service]
Type=simple
ExecStart=ve-mqtt --device Mobile-1 --tty /dev/ttyAMA0 --broker xxxxx --port 8883 --username mqtt --password xxxxxxxxxx --tls
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```
Reload and start the service:
```commandline
sudo systemctl daemon-reload
sudo systemctl enable ve-mqtt
sudo systemctl start ve-mqtt
```

## Development:
Sending test data is easy using socat:
```commandline
socat -d -d PTY,raw,echo=0,link=/tmp/vmodem0 PTY,raw,echo=0,link=/tmp/vmodem1
```
```commandline
cat tests/smartsolar_1.39.dump > /tmp/vmodem0
```
Data will now be available at `/tmp/vmodem1`

## Credits
- [changyuheng/aioserial](https://github.com/changyuheng/aioserial) - async serial implementation
- [karioja/vedirect](https://github.com/karioja/vedirect) - decoding of ve.direct and the example test file
- [sbtinstruments/asyncio-mqtt](https://github.com/sbtinstruments/asyncio-mqtt) async mqtt implementation