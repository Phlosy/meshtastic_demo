import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.data import generate_1kb_data

if __name__ == "__main__":
    data = generate_1kb_data()
    print(data)

