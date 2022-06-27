import argparse
import asyncio
import ssl
import logging

from . import AsyncIOVeDirectMqtt

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)8s] - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

def main():
    parser = argparse.ArgumentParser(description="Async implementation of ve.direct to mqtt")
    parser.add_argument('--tty', help='Serial port', required=True)
    parser.add_argument('--name', help='MQTT device Identifier', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', help='Run with verbose logging')
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    parser.add_argument('--broker', help='MQTT broker hostname', type=str, required=True)
    parser.add_argument('--port', help='MQTT broker port', type=int, default=1883)
    parser.add_argument('--username', help='MQTT broker username', default=None)
    parser.add_argument('--password', help='MQTT broker password', default=None)
    parser.add_argument('--tls', dest='tls_protocol', help='Use TLS for MQTT communication', action='store_const', default=None, const=ssl.PROTOCOL_TLS)
    parser.add_argument('--tls1.2', dest='tls_protocol', help='Use TLS version 1.2 for MQTT communication', action='store_const', default=None, const=ssl.PROTOCOL_TLSv1_2)
    parser.add_argument('--ca_path', help='Custom TLS CA path', default=None)

    args = parser.parse_args()
    if args.verbose:
        global formatter
        ch.setLevel(logging.DEBUG)
    logger.debug(args)
    asyncio.run(AsyncIOVeDirectMqtt(**vars(args)).run())

if __name__ == "__main__":
    main()