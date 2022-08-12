# semtech-loratool
This util sends encrypted lorapackets using the semtech udp-protocol to the network server.


# Dependencies
- [impacket](https://github.com/SecureAuthCorp/impacket)
- [adafruit-circuitpython-tinylora](https://github.com/adafruit/Adafruit_CircuitPython_TinyLoRa)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

# Usage
1. Install the dependencies:
   ```
    pip3 install -r requirements.txt
    ```
2. Clone the repository
3. Set the required environment variables in the file "src/example.env" and rename it to ".env"
4. Execute main.py with command line parameters:
    - `-m` followed by the message to be sent (mandatory)
    - `-f` followed bt the framecount (mandatory)
    - `-v` for verbose output (optional)
    - `-d` for a dryrun (packet will
be generated but not sent) (optional)
    ```
    cd src
    ./main.py -m "01AB" -f 123 -v
    ```


The program will then:
1. encrypt the provided message/payload
2. calculate the MIC (Message Integrity Code),
3. construct the PHYPayload,
4. encode it to base64,
5. construct the UDP PUSH_DATA message,
6. send the UDP datagram to the specified IP address and port using UDP. (unless the command line parameter -d is passed)

# Additional Info

- A lot of parameters that can be individually set in PHYPayload or the UDP message have been hardcoded to be equal to observed parameters in our testbed. Future versions of this tool might make this further customizable.

# Resources
- [LoraWAN specification](https://lora-alliance.org/wp-content/uploads/2020/11/lorawantm_specification_-v1.1.pdf)
- Lora-net/[packet_forwarder](https://github.com/Lora-net/packet_forwarder/)
