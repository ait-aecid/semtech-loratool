"""
`datagramsender`
======================================================
Contains the function to send a UDP Datagram.
* Author(s): tkraner
"""

import socket

def send_datagram(data: bytes, ip, port):
    """ Sends the given data (as bytes!) to the specified ip and port. """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(data, (ip, port)) 
    s.close()