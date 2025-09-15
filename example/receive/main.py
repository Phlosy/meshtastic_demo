import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.loader import load_config
# from my_meshtastic.message.send import send_message
from my_meshtastic.message.receive import listen
import meshtastic
import meshtastic.serial_interface

def main():

    devinfo=load_config("config/config.yaml")
    print(devinfo)
    print("正在监听设备:", devinfo['dev_path']['dev1'])
    # send_message(devinfo['dev1'], "Hello, World!", devinfo['dev2_id'])
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev_path']['dev1'])
    listen(interface)


if __name__ == "__main__":
    main()