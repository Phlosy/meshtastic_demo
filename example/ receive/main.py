import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from my_meshtastic.loader import load_config
from my_meshtastic.message.receive import listen

def main():
    devinfo=load_config("config/device.yaml")
    print(devinfo)
    listen(devinfo['dev1'])
    


if __name__ == "__main__":
    main()