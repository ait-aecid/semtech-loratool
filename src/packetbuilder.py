"""
`packetbuilder`
======================================================
Supplies all the functions for building a udp message to be
sent to the application server
* Author(s): tkraner
"""

import base64
import string
import struct
from binascii import unhexlify
from impacket.crypto import AES_CMAC
from adafruit_tinylora.adafruit_tinylora_encryption import AES
# from datetime import datetime
from datagramsender import send_datagram

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
        new_string += hex_string[x + 1]
    if verbose:
        print(f'New String: {new_string}')
    return new_string
    

def form_phy_payload(appskey: string, nwkskey: string, devaddr: string, unenc_msg: string, fcnt: int):
    """ Constructs a Base64-encoded PHYPayload given the hard coded parameters above """

    global phypayloadsize # global variable to forward the payload size to the packet formatter

    # Encrypts the message using the adafruit_tinylora implementation of AES.
    # (https://github.com/adafruit/Adafruit_CircuitPython_TinyLoRa)
    encryptor = AES(unhexlify(reverse_hex_order(devaddr)), unhexlify(appskey), unhexlify(nwkskey), fcnt) 
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
    returnstring = struct.pack('<Q', number).hex().upper()[:4]
    if verbose:
        print(f'Little endian representation of {number}: {returnstring}')
    return returnstring

def string_to_hex_string(text: string):
    """ Takes a string, encodes it into an uppercase hex string """
    return text.encode().hex().upper()

def form_udp_message(phypayload: string, gateway_eui):
    """ Formats the given PHYPayload string into the required
        UDP PUSH-DATA message format. 
        Formatting info derived from https://github.com/Lora-net/packet_forwarder/blob/master/PROTOCOL.TXT
        and reverse engineering """

    json_obj = f'{{"rxpk":[{{"tmst":3003866827,"time":"2022-08-10T10:00:17.256635Z","chan":1,"rfch":1,"freq":868.300000,"stat":1,"modu":"LORA","datr":"SF7BW125","codr":"4/5","lsnr":10.5,"rssi":-49,"size":19,"data":"{phypayload}"}}]}}'
    json_obj = string_to_hex_string(json_obj)
    protocol_vers = unhexlify('01').hex()
    rand_tok =  unhexlify('1234').hex()
    push_data = unhexlify('00').hex()
    message = f'{protocol_vers}{rand_tok}{push_data}{gateway_eui}{json_obj}' 
    if verbose:
        print(f'UDP PUSH-DATA message = {message}')
    return message