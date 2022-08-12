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

import os
import sys
import getopt
from dotenv import load_dotenv
from binascii import unhexlify
from packetbuilder import form_phy_payload, form_udp_message
from datagramsender import send_datagram


def main(argv):
    message = ''
    fcnt = 0
    verbose = False
    dryrun = False
    try:
      opts, args = getopt.getopt(argv,"m:f:vhd")
    except getopt.GetoptError:
      print('main.py -m <message> -f <framecount> [-v] [-d]')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('main.py -m <message> -f <framecount> [-v] [-d]')
         sys.exit()
      elif opt in ("-m"):
         message = arg
      elif opt in ("-f"):
         fcnt = int(arg)
      elif opt in ("-v"):
         verbose = True
      elif opt in ("-d"):
         dryrun = True

    print(message)
    print(fcnt)
    print(type(fcnt))
    print(verbose)
    # Loading secrets from the .env file
    load_dotenv()
    appskey = os.getenv('APPSKEY')
    nwkskey = os.getenv('NWKSKEY')
    devaddr = os.getenv('DEVADDR')
    target_ip = os.getenv('TARGET_IP')
    target_port = int(os.getenv('TARGET_PORT'))
    gateway_eui = os.getenv('GATEWAY_EUI')

    # Generating the UDP message 
    phy_payload = form_phy_payload(appskey, nwkskey, devaddr, message, fcnt, verbose = verbose)
    udp_message = form_udp_message(phy_payload, gateway_eui, verbose)

    # Sending the UDP message
    if(not dryrun):
        send_datagram(unhexlify(udp_message), target_ip, target_port)
        print('Datagram sent!')

if __name__ == "__main__":
   main(sys.argv[1:])