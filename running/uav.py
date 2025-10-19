import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import meshtastic
import meshtastic.serial_interface
import threading
import time

from my_meshtastic.loader import load_config
from my_meshtastic.message.send import UavInterfaceSender
from my_meshtastic.message.receive import UavInterfaceReceiver
from my_meshtastic.data import UAVWrapper

def main(uav_id, num_interfaces):
 
    # ---------------------------------------------- 加载配置 ----------------------------------------------
    devinfo = load_config("config/config.yaml")

    # 获取本地设备路径
    local_dev_path = []
    for i in range(num_interfaces):
        local_dev_path.append(devinfo["dev_path"]["dev"+str(i+1)])

    # 获取连接的 uav/sys 设备ID
    uav_ids= []
    sys_ids= []
    for i in range(num_interfaces):
        uav_ids.append(devinfo["dev_id"]["uav"+str(i+1)])
        sys_ids.append(devinfo["dev_id"]["hub"+str(i+1)])

    print(local_dev_path,"\n")
    print(uav_ids,"\n")
    print(sys_ids,"\n")

    print(f"⚙️ 计划创建 uav{uav_id} Meshtastic 接口\n")

    spawned_threads = []

    # 创建meshtastic接口
    try:
        dev_path = local_dev_path[uav_id-1]
        interface = meshtastic.serial_interface.SerialInterface(devPath=dev_path)
    except Exception as e:
        print(f"❌ 创建 uav{uav_id} 接口失败: {e}\n")
        sys.exit(1)

    try:
        uav_interface_receiver = UavInterfaceReceiver(interface)
    except Exception as e:
        print(f"❌ 创建 uav{uav_id} 接口接收器失败: {e}\n")
        sys.exit(1)

    try:
        uav_interface_sender = UavInterfaceSender(interface)
    except Exception as e:
        print(f"❌ 创建 uav{uav_id} 接口发送器失败: {e}\n")
        sys.exit(1)

    t_recv = threading.Thread(
        target=uav_receive, args=(uav_interface_receiver,), daemon=True
    )
    t_recv.start()
    spawned_threads.append(t_recv)

    # t_send = threading.Thread(
    #     target=uav_send, args=(uav_interface_sender, sys_ids[uav_id-1]), daemon=True
    # )
    # t_send.start()
    # spawned_threads.append(t_send)

    # 仅测试用
    time.sleep(2)

    for _ in range(10):
        uav_send(uav_interface_sender, sys_ids[uav_id-1])
        time.sleep(2)  # 可根据需要调整发送间隔

def uav_send(uav_interface_sender,sys_id):
    """
    加载配置
    生成UAV状态数据demo
    创建meshtastic接口
    发送到sys上的设备
    """

    # 生成UAV状态数据demo
    uav_data = UAVWrapper.generate_data_demo(1)
    print(uav_data)

    data = UAVWrapper.serialize(uav_data)
    print(len(data))
    # 发送到sys上的设备
    uav_interface_sender.send_payload(data, sys_id)


def uav_receive(uav_interface_receiver):
    """
    从全局接收队列获取 Meshtastic 消息，打印
    """
    try:
        while True:
            msg = uav_interface_receiver.receive_message()  # 阻塞直到收到消息（listen 线程产出）

            if msg is None:
                time.sleep(0.05)
                continue
            print("📥 接收自 Meshtastic:", msg, "\n")

    except Exception as e:
        print(f"❌ uav_receive 出错: {e}\n")

if __name__ == "__main__":
    uav_id = None
    num_interfaces = 4

    if len(sys.argv) ==2:
        uav_id = int(sys.argv[1])
    elif len(sys.argv) > 2:
        uav_id = int(sys.argv[1])
        num_interfaces = int(sys.argv[2])
    else:
        print("🔴 参数输入错误，请输入正确参数，例如：python uav.py 1 4\n")
        sys.exit(1)

    main(uav_id, num_interfaces)