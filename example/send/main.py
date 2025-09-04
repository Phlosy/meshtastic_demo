import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.loader import load_config
from my_meshtastic.message.send import send_message
import time
import meshtastic
import meshtastic.serial_interface


def main():
    source_dev= "dev2"
    devinfo=load_config("config/device.yaml")
    print(devinfo)
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo[source_dev])
    for i in range(10):
        send_message(interface, "Hello", devinfo['dev3_id'])
        send_message(interface, "Hello", devinfo['dev4_id'])
        time.sleep(1)
    interface.close()
    


if __name__ == "__main__":
    main()