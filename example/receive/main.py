import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.loader import load_config
# from my_meshtastic.message.send import send_message
from my_meshtastic.message.receive import listen
import meshtastic
import meshtastic.serial_interface

def main():
    devinfo=load_config("config/device.yaml")
    print(devinfo)
    # send_message(devinfo['dev1'], "Hello, World!", devinfo['dev2_id'])
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev2'])
    listen(interface)


if __name__ == "__main__":
    main()