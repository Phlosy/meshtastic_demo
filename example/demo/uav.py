import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.data import UavData
from my_meshtastic.loader import load_config
import meshtastic
import meshtastic.serial_interface
from my_meshtastic.message.send import send_message
import json
from my_meshtastic.message.receive import listen

def main():
 
    # 加载配置
    devinfo=load_config("config/config.yaml")
    # print(devinfo)

    # 创建meshtastic接口
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev_path']['dev1'])

    # 发送UAV状态数据
    import multiprocessing
    import time

    def send_loop(interface, destdev):
        for _ in range(10):
            uav_send(interface, destdev)
            time.sleep(2)  # 可根据需要调整发送间隔

    # 创建接收进程
    recv_process = multiprocessing.Process(target=uav_receive, args=(interface,))
    # 创建发送进程
    send_process = multiprocessing.Process(target=send_loop, args=(interface, devinfo['dev_id']['hub1']))

    # 启动进程
    recv_process.start()
    send_process.start()

    # 等待发送进程结束
    send_process.join()
    # 接收进程可根据需要决定是否终止，这里简单处理为主进程结束时一同结束

def uav_send(interface,destdev):
    """
    加载配置
    生成UAV状态数据demo
    创建meshtastic接口
    发送到sys上的设备
    """

    # 生成UAV状态数据demo
    uav_data = UavData.generate_uav_data_demo(1)
    print(uav_data)

    # 转换为json
    data = json.dumps(uav_data,ensure_ascii=False)
    print(len(data))

    # 发送到sys上的设备
    send_message(interface, data, destdev)


def uav_receive(interface):
    """
    监听meshtastic设备
    接收UAV状态数据
    打印
    """
    listen(interface)

if __name__ == "__main__":
    main()