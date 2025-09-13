import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.data import UavData
from my_meshtastic.loader import load_config
import meshtastic
import meshtastic.serial_interface
from my_meshtastic.message.send import send_message
import json


def main():
    """

    加载配置
    生成UAV状态数据demo
    创建meshtastic接口
    发送到sys上的设备
    
    """
    # 加载配置
    devinfo=load_config("config/config.yaml")
    # print(devinfo)

    # 发送UAV状态数据
    uav_send(devinfo)

def uav_send(devinfo):
    # 生成UAV状态数据demo
    uav_data = UavData.generate_uav_data_demo(1)
    print(uav_data)

    data = json.dumps(uav_data,ensure_ascii=False)
    print(len(data))

    # 创建meshtastic接口
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev_path']['dev1'])

    # 发送到sys上的设备
    send_message(interface, data, devinfo['dev_id']['hub1'])


if __name__ == "__main__":
    main()