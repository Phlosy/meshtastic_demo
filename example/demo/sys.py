import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import meshtastic
import meshtastic.serial_interface
import threading
import time

from my_meshtastic.loader import load_config
from my_meshtastic.message.receive import receive_meshtastic_message, listen
from my_meshtastic.message.send import send_message
from my_meshtastic.mqtt import MQTTClient


def main():
    # 加载配置
    devinfo=load_config("config/config.yaml")
    print(devinfo)

    # 创建meshtastic接口
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev_path']['dev1'])

    # 启动后台线程监听meshtastic设备
    listener_thread = threading.Thread(target=listen, args=(interface,), daemon=True)
    listener_thread.start()

    # 连接到mqtt
    mqtt_uav_client = MQTTClient(broker="localhost", port=1883, topic="demo/uav")
    mqtt_uav_client.connect()

    mqtt_sys_client = MQTTClient(broker="localhost", port=1883, topic="demo/sys")
    mqtt_sys_client.connect()

    # 等待2秒
    time.sleep(2)

    # 接收数据
    sys_receive_thread = threading.Thread(target=sys_receive, args=(interface, mqtt_uav_client))
    sys_receive_thread.start()


    sysloopthread = threading.Thread(target=mqtt_sys_client.loop_forever)
    sysloopthread.start()

    # 发送mqtt数据到uav设备
    sys_send_thread = threading.Thread(target=sys_send, args=(interface, mqtt_sys_client, devinfo))
    sys_send_thread.start()


def sys_receive(interface, mqtt_uav_client):
    """
    持续监听设备
    获取UAV状态数据
    发布到MQTT
    """
    # print("开始接收消息...")
    try:
        while True:
            message = receive_meshtastic_message()  # 会阻塞直到有消息
            print("✅ 收到消息:", message)

            # 如果需要转发到 MQTT，这里处理即可
            mqtt_uav_client.publish(message)

    except KeyboardInterrupt:
        print("🔴 手动停止监听")
        interface.close()



def sys_send(interface, mqtt_sys_client, devinfo):
    """
    监听MQTT
    获取灯塔系统计算结果
    发送给UAV设备
    """
    while True:
        message = mqtt_sys_client.receive_mqtt_message()
        print("✅ 收到消息:", message)
        send_message(interface, message, devinfo['dev_id']['uav1'])
    

if __name__ == "__main__":
    main()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🔴 手动退出")