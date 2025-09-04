import sys
import os
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from my_meshtastic.loader import load_config
from my_meshtastic.message.receive import listen
from my_meshtastic.message.send import send_message
import meshtastic
import meshtastic.serial_interface


def main():
    devinfo = load_config("config/device.yaml")
    print(devinfo)

    # 只用一个 Meshtastic 节点
    interface = meshtastic.serial_interface.SerialInterface(devPath=devinfo['dev1'])

    # 启动后台线程监听消息
    listener_thread = threading.Thread(target=listen, args=(interface,), daemon=True)
    listener_thread.start()
    print("开始监听消息...")
    time.sleep(1)
    
    for i in range(10):
        send_message(interface, "Hello" + str(i), devinfo['dev1_id'])
        time.sleep(2)
  
    # print("消息发送完毕，保持接收3秒后退出")

    time.sleep(1000)  # 保持接收
    interface.close()

if __name__ == "__main__":
    main()
