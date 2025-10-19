import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from my_meshtastic.loader import load_config
from my_meshtastic.data import UAVWrapper
from my_meshtastic.mqtt import MQTTClient
import json


def main():
    num_interfaces = 4

    devinfo = load_config("config/config.yaml")
    print(f"🔧 配置加载完成: {devinfo}\n")

    # 获取本地设备路径
    local_dev_path=[]
    for i in range(num_interfaces):
        local_dev_path.append(devinfo["dev_path"]["dev"+str(i+1)])

    # 获取远端连接的uav设备ID
    uav_ids=[]
    for i in range(num_interfaces):
        uav_ids.append(devinfo["dev_id"]["uav"+str(i+1)])

    sys_ids=[]
    for i in range(num_interfaces):
        sys_ids.append(devinfo["dev_id"]["hub"+str(i+1)])

    print(local_dev_path)
    print(uav_ids)
    print(sys_ids)

    # 初始化客户端
    i=0
    mqtt_client = MQTTClient(broker="localhost", port=1883, topic=f"sys/{sys_ids[0]}")

    # 连接到 broker
    mqtt_client.connect()

    # 发布一条测试消息
    mqtt_client.publish("Hello from class wrapper!")

    # # 进入循环，保持监听
    # mqtt_client.loop_forever()

if __name__ == "__main__":
    main()