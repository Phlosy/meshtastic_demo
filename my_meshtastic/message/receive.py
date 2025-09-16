import meshtastic
import meshtastic.serial_interface
import time
from pubsub import pub
import queue

# 队列保存消息
message_queue = queue.Queue()

def on_receive(packet, interface):
    print("📩 收到消息:", packet)

def on_receive_payload(packet, interface):
    # 文本消息
    text = packet['decoded'].get('text')
    # 原始 payload
    payload = packet['decoded'].get('payload')
    # print(f"📩 收到消息 from {packet['from']} to {packet['to']}: text={text}, payload={payload}")
    if text:
        message_queue.put(text)


def listen(interface):
    # 连接本地设备
    # interface = meshtastic.serial_interface.SerialInterface(devPath=devPath)

    # 注册接收消息的回调
    # interface.onReceive = on_receive
    pub.subscribe(on_receive_payload, "meshtastic.receive")

    print("开始监听消息...")
    try:
        while True:
            time.sleep(0.01)  # 保持主线程运行
    except KeyboardInterrupt:
        print("退出监听")
        interface.close()

def receive_meshtastic_message():
    return message_queue.get()
