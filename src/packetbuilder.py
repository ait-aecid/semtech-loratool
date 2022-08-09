"""
`packetbuilder`
======================================================
Supplies all the functions for building a packet to be
sent to the application server
* Author(s): tkraner
"""

import os
import base64
import string
import struct
from binascii import unhexlify
from impacket.crypto import AES_CMAC
from adafruit_tinylora.adafruit_tinylora_encryption import AES
from datetime import datetime
from dotenv import load_dotenv


mhdr = '80'
fctrl = '82'
fopts = '0306'
fport = '01'

phypayloadsize = 0

verbose = False

def reverse_hex_order(hex_string: string):
    """ Reverses the order of a given hex-string (little endian <-> big endian) """
    if verbose:
        print(f'Original String: {hex_string}')
    new_string = ''
    for x in range(len(hex_string) - 2,  -1, -2):
        new_string += hex_string[x]
        new_string += hex_string[x+1]
    if verbose:
        print(f'New String: {new_string}')
    return new_string
    

def form_phy_payload(appskey: string, nwkskey: string, devaddr: string, unenc_msg: string, fcnt: int):
    """ Constructs a Base64-encoded PHYPayload given the hard coded parameters above """

    global phypayloadsize # global variable to forward the payload size to the packet formatter

    # Encrypts the message using the adafruit_tinylora implementation of AES.
    # (https://github.com/adafruit/Adafruit_CircuitPython_TinyLoRa)
    encryptor = AES(unhexlify(reverse_hex_order(devaddr)), unhexlify(appskey), unhexlify(nwkskey), fcnt) #0x010F calculate_fcnt(fcnt, 'big'
    encr_msg = encryptor.encrypt(bytearray.fromhex(unenc_msg))
    if verbose:
        print(f'Encrypted message = {encr_msg.hex().upper()}')

    # Formation of the PHYPayload without MIC to calculate MIC.
    phypayload = mhdr + devaddr + fctrl + calculate_fcnt(fcnt) + fopts + fport + encr_msg.hex().upper()

    # Constructing the B0 parameter for calculating the MIC as defined in the LoRaWAN Specification
    # (https://lora-alliance.org/wp-content/uploads/2020/11/lorawantm_specification_-v1.1.pdf).
    littlend = calculate_fcnt(fcnt)
    b0 = f'490000000000{devaddr}{littlend}000000' + (len(phypayload) // 2).to_bytes(1, byteorder='big').hex().upper()

    length = (len(b0) + len(phypayload)) // 2 # Calculating the length of the string for the AES_CMAC operation.

    # Calculating the MIC using the impacket AES_CMAC implementation
    # (https://github.com/SecureAuthCorp/impacket)
    mic = AES_CMAC(unhexlify(nwkskey), unhexlify(b0 + phypayload), length).hex()[:8]
    if verbose:
        print(f'Message Integrity Code (MIC) = {mic}')

    # Appending the MIC to form the final PHYPayload. 
    phypayload += mic.upper()
    phypayloadsize = len(phypayload) // 2
    if verbose:
        print(f'PHYPayload = {phypayload}')
        print(f'PHYPayload size = {phypayloadsize}')

    # Base64 encoding of PHYPayload.
    if verbose:
        print(f'Base64-encoded packet = {base64.b64encode(unhexlify(phypayload)).decode()}')
    return base64.b64encode(unhexlify(phypayload)).decode()

def calculate_fcnt(number: int):
    """ Form the little endian hex string represantation of an int number, max value is 65535 """
    if verbose:
        print(struct.pack('<Q', number).hex().upper()[:4])
    return struct.pack('<Q', number).hex().upper()[:4]


def form_phy_packet(phypayload):
    print('TODO')


load_dotenv()
appskey = os.getenv('APPSKEY')
nwkskey = os.getenv('NWKSKEY')
devaddr = os.getenv('DEVADDR')

print(form_phy_payload(appskey, nwkskey, devaddr, '01da', 271))