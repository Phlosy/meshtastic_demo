import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.loader import load_config
from my_meshtastic.message.send import send_message

def main():
    devinfo=load_config("config/device.yaml")
    print(devinfo)
    send_message(devinfo['dev1'], "Hello", devinfo['dev2_id'])
    


if __name__ == "__main__":
    main()