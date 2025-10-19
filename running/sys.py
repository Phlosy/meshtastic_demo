import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
import meshtastic
import meshtastic.serial_interface

from my_meshtastic.loader import load_config
from my_meshtastic.mqtt import MQTTClient
from my_meshtastic.data import UAVWrapper
from my_meshtastic.message.receive import SysInterfaceReceiver
from my_meshtastic.message.send import SysInterfaceSender

def main(num_interfaces: int):
    """
    主入口函数
    :param num_interfaces: 要创建的 Meshtastic 接口数量，默认 4
    """

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

    print(f"⚙️ 计划创建 {num_interfaces} 个 Meshtastic 接口\n")

    # ---------------------------------------------- 初始化每个接口 ----------------------------------------------
    broker_host = devinfo.get("broker", {}).get("host", "localhost")
    broker_port = devinfo.get("broker", {}).get("port", 1883)

    sys_interface_receivers = []
    sys_interface_senders = []
    spawned_threads = []   # 启动过的线程，方便管理

    for i in range(num_interfaces):
        # 创建Meshtastic接口
        try:
            dev_path = local_dev_path[i]
            interface = meshtastic.serial_interface.SerialInterface(devPath=dev_path)

            print(f"✅ 创建 {local_dev_path[i]} 接口成功\n")

        except Exception as e:
            print(f"❌ 创建 {local_dev_path[i]} 接口失败: {e}\n")
            continue

        # 为该接口创建一个独立的UAV MQTT客户端
        try:
            uav_topic = f"uav/{uav_ids[i]}"  # 每个接口各用一个主题，方便区分

            # 监听灯塔的sys的topic
            uav_client = MQTTClient(broker=broker_host, port=broker_port, topic=uav_topic)
            uav_client.connect()

            print(f"✅ 创建UAV MQTT主题{uav_topic}成功\n")

        except Exception as e:
            print(f"❌ 创建UAV MQTT主题{uav_topic}失败: {e}\n")
            continue

        # 创建SysInterfaceReceiver
        try:
            sys_interface_receiver = SysInterfaceReceiver(
                interface=interface,
                uav_client=uav_client,
            )

            sys_interface_receivers.append(sys_interface_receiver)

            print(f"✅ 创建SysInterfaceReceiver{sys_interface_receiver.interface.devPath}成功\n")

        except Exception as e:
            print(f"❌ 创建SysInterfaceReceiver{sys_interface_receiver.interface.devPath}失败: {e}\n")
            continue

        # 创建SYS MQTT客户端
        try:
            sys_topic = f"sys/{sys_ids[i]}"  # 每个接口各用一个主题，方便区分
            # 发送uva的消息至topic
            sys_client = MQTTClient(broker=broker_host, port=broker_port, topic=sys_topic)
            sys_client.connect()
            print(f"✅ 创建SYS MQTT主题{sys_topic}成功\n")

        except Exception as e:
            print(f"❌ 创建SYS MQTT主题{sys_topic}失败: {e}\n")
            continue

        # 创建SysInterfaceSender
        try:
            sys_interface_sender = SysInterfaceSender(
                interface=interface,
                sys_client=sys_client,
            )

            sys_interface_senders.append(sys_interface_sender)

            print(f"✅ 创建SysInterfaceSender{sys_interface_sender.interface.devPath}成功\n")

        except Exception as e:
            print(f"❌ 创建SysInterfaceSender{sys_interface_sender.interface.devPath}失败: {e}\n")
            continue

        print(f"✅ 初始化{local_dev_path[i]}接口成功\n")

    # 如果全部失败，直接退出
    if not sys_interface_receivers or not sys_interface_senders:
        print("🔴 没有任何接口初始化成功，程序退出")
        return

    # ---------------------------------------------- 为成功的每对 (interface, mqtt_client) 启动收发线程 ----------------------------------------------
    for i in range(num_interfaces):
        t_recv = threading.Thread(
            target=sys_receive, args=(sys_interface_receivers[i],), daemon=True
        )
        t_recv.start()
        spawned_threads.append(t_recv)

        t_send = threading.Thread(
            target=sys_send, args=(sys_interface_senders[i], uav_ids[i]), daemon=True
        )
        t_send.start()
        spawned_threads.append(t_send)

    print(f"✅ 已启动 {len(sys_interface_receivers)} 个接口的监听与收发线程\n")

    # 3) 主线程保持存活（也可改为 join 所有非守护线程）
    try:
        while True:
            time.sleep(1)
            # print("🔍 当前线程数量:", len(spawned_threads), "\n")
    except KeyboardInterrupt:
        print("🔴 手动退出\n")
        # 可选：关闭资源
        for sys_interface_receiver in sys_interface_receivers:
            try:
                sys_interface_receiver.close()
            except Exception:
                pass
        for sys_interface_sender in sys_interface_senders:
            try:
                sys_interface_sender.close()
            except Exception:
                pass


def sys_receive(sys_interface_receiver):
    """
    从全局接收队列获取 Meshtastic 消息，发布到该接口对应的 MQTT topic
    """
    try:
        while True:
            msg = sys_interface_receiver.receive_message()  # 阻塞直到收到消息（listen 线程产出）

            if msg is None:
                time.sleep(0.05)
                continue
            print("📥 接收自 Meshtastic:", msg, "\n")

            # 发布到MQTT
            sys_interface_receiver.uav_client.publish(msg)
    except Exception as e:
        print(f"❌ sys_receive 出错: {e}\n")
        


def sys_send(sys_interface_sender, uav_id):
    """
    从该接口对应的 MQTT topic 获取系统消息，转发给指定 UAV 设备
    """
    while True:
        try:
            msg = sys_interface_sender.sys_client.receive_mqtt_message()  # 阻塞/或短暂等待
            if msg is None:
                time.sleep(0.05)
                continue

            # 如果msg为str，转化为bytes
            if isinstance(msg, str):
                bytes_msg = UAVWrapper.serialsize(msg)
            else:
                bytes_msg = msg

            print("📤 从 MQTT 收到系统消息:", msg, "\n")

            sys_interface_sender.send_payload(bytes_msg, uav_id)
        except Exception as e:
            print(f"❌ sys_send 出错: {e}\n")
            time.sleep(0.2)


if __name__ == "__main__":
    # 默认 4 个
    num_interfaces = 4
    if len(sys.argv) > 1:
        try:
            num_interfaces = int(sys.argv[1])
        except ValueError:
            print("🔴 请输入有效的数字，例如：python sys.py 4\n")
            sys.exit(1)

    main(num_interfaces)
