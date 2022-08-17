#!/usr/bin/env python3

"""
`main`
======================================================
Entrypoint for the semtech-loratool. Takes the message (hex-format) and the
framecount (int number) as required command line arguments. [-v] and [-d]
can be supplied as additional arguments for verbosity and dryrun (packet will
be generated but not sent) respectively. Help is accessed with [-h].
* Author(s): tkraner
"""

import argparse
import os
import socket
import sys
from binascii import unhexlify

from dotenv import load_dotenv

from packetbuilder import form_phy_payload, form_udp_message


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("message", type=str, help="message to be sent as a hex string")
    parser.add_argument("fcnt", type=int, help="current framecount")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        help="generate the UDP message without sending it",
        action="store_true",
    )
    args = parser.parse_args()
    message = args.message
    fcnt = args.fcnt
    verbose = args.verbosity
    dryrun = args.dryrun

    # Loading secrets from the .env file
    load_dotenv()
    appskey = os.getenv("APPSKEY")
    nwkskey = os.getenv("NWKSKEY")
    devaddr = os.getenv("DEVADDR")
    target_ip = os.getenv("TARGET_IP")
    target_port = int(os.getenv("TARGET_PORT"))
    gateway_eui = os.getenv("GATEWAY_EUI")

    # Generating the UDP message
    phy_payload = form_phy_payload(
        appskey, nwkskey, devaddr, message, fcnt, verbose=verbose
    )
    udp_message = form_udp_message(phy_payload, gateway_eui, verbose)

    # Sending the UDP message
    if not dryrun:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(unhexlify(udp_message), (target_ip, target_port))
        s.close()
        print("Datagram sent!")


if __name__ == "__main__":
    main(sys.argv[1:])
