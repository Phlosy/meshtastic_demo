import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
import meshtastic
import meshtastic.serial_interface

from my_meshtastic.loader import load_config
from my_meshtastic.message.receive import receive_meshtastic_message, listen
from my_meshtastic.message.send import send_message
from my_meshtastic.mqtt import MQTTClient


def main(num_interfaces: int):
    """
    主入口函数
    :param num_interfaces: 要创建的 Meshtastic 接口数量，默认 4
    """
    devinfo = load_config("config/config.yaml")
    print(f"🔧 配置加载完成: {devinfo}\n")
    print(f"⚙️ 计划创建 {num_interfaces} 个 Meshtastic 接口\n")

    interfaces = []        # 成功创建的 meshtastic 接口
    mqtt_clients = []      # 与每个接口配对的 mqtt 客户端
    uav_ids = []           # 与每个接口配对的目标 UAV ID（示例：uav1/uav2...）
    spawned_threads = []   # 我们启动过的线程，方便管理

    # 1) 初始化每个接口 & 对应的 MQTT client
    for i in range(num_interfaces):
        dev_key = f"dev{i+1}"
        if dev_key not in devinfo["dev_path"]:
            print(f"⚠️ 配置文件缺少 {dev_key}，跳过\n")
            continue

        dev_path = devinfo["dev_path"][dev_key]
        print(f"⚙️ 创建 {dev_key} 接口: {dev_path}\n")

        try:
            interface = meshtastic.serial_interface.SerialInterface(devPath=dev_path)
            interfaces.append(interface)

            # 启动 meshtastic 监听线程（监听串口，向 receive 队列投递）
            t = threading.Thread(target=listen, args=(interface,), daemon=True)
            t.start()
            spawned_threads.append(t)
        except Exception as e:
            print(f"❌ 创建 {dev_key} 接口失败: {e}\n")
            continue

        # 为该接口创建一个独立的 MQTT 客户端
        try:
            mqtt_topic = f"demo/uav{i+1}"  # 每个接口各用一个主题，方便区分
            client = MQTTClient(
                broker=devinfo.get("broker", {}).get("host", "localhost"),
                port=devinfo.get("broker", {}).get("port", 1883),
                topic=mqtt_topic,
            )
            client.connect()
            mqtt_clients.append(client)

            # 每个 client 只启动一次 loop_forever 线程
            t = threading.Thread(target=client.loop_forever, daemon=True)
            t.start()
            spawned_threads.append(t)
        except Exception as e:
            print(f"❌ MQTT 客户端初始化失败: {e}\n")
            # 该接口就不要继续了
            interfaces.pop()  # 保持一一对应
            continue

        # 记录该接口对应的 UAV 目标ID（示例：uav1/uav2...，依据你的配置）
        uav_key = f"uav{i+1}"
        if "dev_id" in devinfo and uav_key in devinfo["dev_id"]:
            uav_ids.append(devinfo["dev_id"][uav_key])
        else:
            # 找不到就退回到 uav1，或者你也可以选择跳过
            uav_ids.append(devinfo["dev_id"].get("uav1"))

    # 如果全部失败，直接退出
    if not interfaces:
        print("🔴 没有任何接口初始化成功，程序退出")
        return

    time.sleep(1.5)  # 给 listener/mqtt loop 一点点缓冲时间

    # 2) 为成功的每对 (interface, mqtt_client) 启动收发线程
    for idx, (interface, client) in enumerate(zip(interfaces, mqtt_clients)):
        # 接收：从 receive 队列里拿 Meshtastic 消息 -> 发布到该接口对应的 MQTT topic
        t_recv = threading.Thread(
            target=sys_receive, args=(interface, client), daemon=True
        )
        t_recv.start()
        spawned_threads.append(t_recv)

        # 发送：从该接口对应的 MQTT topic 收系统消息 -> 发回 Meshtastic 设备
        target_uav_id = uav_ids[idx] if idx < len(uav_ids) else devinfo["dev_id"]["uav1"]
        t_send = threading.Thread(
            target=sys_send, args=(interface, client, target_uav_id), daemon=True
        )
        t_send.start()
        spawned_threads.append(t_send)

    print(f"✅ 已启动 {len(interfaces)} 个接口的监听与收发线程\n")

    # 3) 主线程保持存活（也可改为 join 所有非守护线程）
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🔴 手动退出\n")
        # 可选：关闭资源
        for itf in interfaces:
            try:
                itf.close()
            except Exception:
                pass


def sys_receive(interface, mqtt_client):
    """
    从全局接收队列获取 Meshtastic 消息，发布到该接口对应的 MQTT topic
    """
    try:
        while True:
            msg = receive_meshtastic_message()  # 阻塞直到收到消息（listen 线程产出）
            if msg is None:
                time.sleep(0.05)
                continue
            print("📥 接收自 Meshtastic:", msg, "\n")
            mqtt_client.publish(msg)
    except Exception as e:
        print(f"⚠️ sys_receive 出错: {e}\n")
        try:
            interface.close()
        except Exception:
            pass


def sys_send(interface, mqtt_client, uav_id):
    """
    从该接口对应的 MQTT topic 获取系统消息，转发给指定 UAV 设备
    """
    while True:
        try:
            msg = mqtt_client.receive_mqtt_message()  # 阻塞/或短暂等待
            if msg is None:
                time.sleep(0.05)
                continue
            print("📤 从 MQTT 收到系统消息:", msg, "\n")
            send_message(interface, msg, uav_id)
        except Exception as e:
            print(f"⚠️ sys_send 出错: {e}\n")
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
