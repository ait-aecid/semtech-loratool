import os
from dotenv import load_dotenv
from binascii import unhexlify
from packetbuilder import form_phy_payload, form_udp_message
from datagramsender import send_datagram

# Message in hexadecimal representation
message = "01da"

# Frame counter value
fcnt = 282


# Loading secrets from the .env file
load_dotenv()
appskey = os.getenv('APPSKEY')
nwkskey = os.getenv('NWKSKEY')
devaddr = os.getenv('DEVADDR')
target_ip = os.getenv('TARGET_IP')
target_port = int(os.getenv('TARGET_PORT'))
gateway_eui = os.getenv('GATEWAY_EUI')

# Generating the UDP message 
phy_payload = form_phy_payload(appskey, nwkskey, devaddr, message, fcnt)
udp_message = form_udp_message(phy_payload, gateway_eui)

# Sending the UDP message
send_datagram(unhexlify(udp_message), target_ip, target_port)