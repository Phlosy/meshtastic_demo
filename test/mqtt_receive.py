import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from my_meshtastic.loader import load_config
from my_meshtastic.data import UavData
from my_meshtastic.mqtt import MQTTClient
import json

def main():
    devinfo=load_config("config/config.yaml")
    print(devinfo)

    uva_data = UavData.generate_uav_data_demo(2)
    print(json.dumps(uva_data, indent=2, ensure_ascii=False))

    # 初始化客户端
    mqtt_client = MQTTClient(broker="localhost", port=1883, topic="test/topic")

    # 连接到 broker
    mqtt_client.connect()

    # 订阅一条测试消息
    # mqtt_client.subscribe("test/topic")

    # # 进入循环，保持监听
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()