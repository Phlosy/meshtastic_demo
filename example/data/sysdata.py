import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.data import SysWrapper

def main():
    data = SysWrapper.generate_data_demo()
    # print(data)
    # print(SysWrapper.to_json(data))

    raw_bytes = SysWrapper.serialize(data)
    print(len(raw_bytes))
    print(SysWrapper.deserialize(raw_bytes))

if __name__ == "__main__":
    main()

