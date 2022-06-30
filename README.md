# asyncio-vedirect-mqtt

This is a simple program for publishing serial data from the Victron VE.Direct protocol
to an mqtt broker in an asynchronous manner. 

This is done using [changyuheng/aioserial](https://github.com/changyuheng/aioserial) to read the serial data and passing it through 
to an async implementation of [karioja/vedirect](https://github.com/karioja/vedirect) to decode the data. This is then sent over MQTT to a 
broker of your choice via [sbtinstruments/asyncio-mqtt](https://github.com/sbtinstruments/asyncio-mqtt).

The implementation supports TLS and authentication when connecting to the MQTT server.

## Getting started:

Download from git with pip
```commandline
pip3 install git+https://github.com/metrafonic/asyncio-vedirect-mqtt.git
```
This will add the `ve-mqtt` executable to `~/.local/bin`.

### Run the code:
```text
$ ve-mqtt -h
usage: ve-mqtt [-h] --tty TTY --topic TOPIC [-v] [--timeout TIMEOUT] --broker BROKER [--port PORT] [--username USERNAME] [--password PASSWORD]
               [--tls] [--tls1.2] [--ca_path CA_PATH]

Async implementation of ve.direct to mqtt

optional arguments:
  -h, --help           show this help message and exit
  --tty TTY            Serial port with incloming ve.direct data
  --topic TOPIC        MQTT topic to publish to
  -v, --verbose        Run with verbose logging
  --timeout TIMEOUT    Serial port read timeout
  --broker BROKER      MQTT broker hostname
  --port PORT          MQTT broker port
  --username USERNAME  MQTT broker username
  --password PASSWORD  MQTT broker password
  --tls                Use TLS for MQTT communication
  --tls1.2             Use TLS version 1.2 for MQTT communication
  --ca_path CA_PATH    Custom TLS CA path

```

### Sending test data:
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