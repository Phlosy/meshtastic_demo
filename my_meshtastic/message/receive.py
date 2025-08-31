import meshtastic
import meshtastic.serial_interface
import time

def on_receive(packet, interface):
    print("📩 收到消息:", packet)

def listen(devPath="/dev/ttyACM0"):
    # 连接本地设备
    interface = meshtastic.serial_interface.SerialInterface(devPath=devPath)

    # 注册接收消息的回调
    interface.onReceive = on_receive

    print("开始监听消息...")
    try:
        while True:
            time.sleep(1)  # 保持主线程运行
    except KeyboardInterrupt:
        print("退出监听")
        interface.close()
