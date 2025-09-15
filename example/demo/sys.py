import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.data import UavData

def main():
    # 加载配置
    devinfo=load_config("config/config.yaml")
    print(devinfo)

    # 生成UAV状态数据demo
    uav_data = UavData.generate_uav_data_demo(3)
    print(uav_data)

def sys_receive(devinfo, interface):
    """
    持续监听设备
    获取UAV状态数据
    发布到MQTT
    """
    # 接收UAV状态数据
    receive_message(interface, devinfo['dev_id']['hub1'])


def sys_send(devinfo, interface):
    """
    监听MQTT
    获取灯塔系统计算结果
    发送给UAV设备
    """
    

if __name__ == "__main__":
    main()