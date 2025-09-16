import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import meshtastic
import meshtastic.serial_interface
import threading
import time

from my_meshtastic.loader import load_config
from my_meshtastic.message.send import send_message
from my_meshtastic.message.receive import listen
from my_meshtastic.data import UAVWrapper

def main():
 
    # 加载配置
    devinfo=load_config("config/config.yaml")
    # print(devinfo)

    # 创建meshtastic接口
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev_path']['dev1'])
    # interface.sendData(data_message, destinationId=target_node_id)
    assert isinstance(interface, meshtastic.serial_interface.SerialInterface), "interface must be a meshtastic.serial_interface.SerialInterface object"

    # 启动后台线程监听消息
    listener_thread = threading.Thread(target=listen, args=(interface,), daemon=True)
    listener_thread.start()

    time.sleep(2)

    for _ in range(10):
        uav_send(interface, devinfo['dev_id']['uav1'])
        time.sleep(2)  # 可根据需要调整发送间隔

    # 创建接收进程
    # recv_process = multiprocessing.Process(target=uav_receive, args=(interface,))
    # 创建发送进程
    # send_process = multiprocessing.Process(target=send_loop, args=(interface, devinfo['dev_id']['uav1']))

    # # 启动进程
    # # recv_process.start()
    # time.sleep(2)
    # send_process.start()

    # # 等待发送进程结束
    # send_process.join()

def uav_send(interface,destdev):
    """
    加载配置
    生成UAV状态数据demo
    创建meshtastic接口
    发送到sys上的设备
    """

    # 生成UAV状态数据demo
    uav_data = UAVWrapper.generate_data_demo(3)
    print(uav_data)

    data = UAVWrapper.serialize(uav_data)
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

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🔴 手动退出")