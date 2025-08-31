import sys
import os
import time
from meshtastic import serial_interface

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from my_meshtastic.loader import load_config

def start_receive(iface):
    """注册接收回调"""
    def on_receive(packet):
        if "text" in packet:
            print(f"📩 收到消息 from {packet.get('fromId')}: {packet['text']}")
        else:
            print(f"📩 收到非文本消息 from {packet.get('fromId')}: {packet}")

    iface.packet_received_callback = on_receive
    # 不再需要 iface.run()，回调会自动异步触发

def start_send(iface, target_id, count=10, interval=1):
    """发送消息"""
    for i in range(count):
        msg = f"Hello {i}"
        iface.sendText(msg, destinationId=target_id)
        print(f"✉️ 发送消息: {msg}")
        time.sleep(interval)

def main():
    devinfo = load_config("config/device.yaml")
    print(devinfo)

    # 只用一个 Meshtastic 节点
    iface = serial_interface.SerialInterface(devPath=devinfo['dev1'])

    # 注册接收回调
    print("开始监听")
    start_receive(iface)
    time.sleep(1)
    
    # 发送消息
    start_send(iface, target_id=devinfo['dev2_id'], count=10, interval=1)

    print("消息发送完毕，保持接收10秒后退出")
    time.sleep(10)  # 保持接收
    iface.close()

if __name__ == "__main__":
    main()
