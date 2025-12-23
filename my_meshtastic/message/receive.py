import meshtastic.serial_interface
import queue
import time
from pubsub import pub
from my_meshtastic.data import UAVWrapper
from my_meshtastic.data import SysWrapper

# ------------------- 接口专属消息接收器 -------------------
# ------------------从mesh设备接受消息---------------------

class SysInterfaceReceiver:
    def __init__(self, interface, uav_client):
        self.interface = interface
        self.queue = queue.Queue()
        self.uav_client = uav_client
        # 订阅全局主题，但用回调里按 interface 过滤
        pub.subscribe(self.on_receive_payload, "meshtastic.receive")
        print(f"✅ 已绑定接口 {getattr(self.interface, 'devPath', '<iface>')}")

    def on_receive_payload(self, packet, interface):
        # 关键：只处理“本接口”的消息，隔离不同串口
        if interface is not self.interface:
            return

        decoded = packet.get('decoded', {}) if isinstance(packet, dict) else {}
        raw_text = decoded.get('text')
        raw_payload = decoded.get('payload')

        try:
            text = raw_text
            # payload = UAVWrapper.deserialize(raw_payload)
            # payload = UAVWrapper.deserialize(raw_payload)
            payload = raw_payload
        except Exception as e:
            print(f"❌ 反序列化失败: {e}")
            # print(f"raw_text: {type(raw_text)}")
            print(f"raw_payload: {type(raw_payload)}")
            return

        print(f"📩 [{getattr(self.interface, 'devPath', '<iface>')}] "
              f"from={packet.get('from')} to={packet.get('to')} text={text} payload={payload}")

        if payload:
            self.queue.put(UAVWrapper.to_json(payload))


    def receive_message(self):
        return self.queue.get()

    def listen_forever(self):
        print(f"开始监听接口 {getattr(self.interface, 'devPath', '<iface>')} ...")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"退出监听 {getattr(self.interface, 'devPath', '<iface>')}")
            self.interface.close()

    def close(self):
        self.interface.close()


class UavInterfaceReceiver:
    def __init__(self, interface):
        self.interface = interface
        self.queue = queue.Queue()

        # 订阅全局主题，但用回调里按 interface 过滤
        pub.subscribe(self.on_receive_payload, "meshtastic.receive")
        print(f"✅ 已绑定接口 {getattr(self.interface, 'devPath', '<iface>')}")

    def on_receive_payload(self, packet, interface):
        # 关键：只处理“本接口”的消息，隔离不同串口  
        if interface is not self.interface:
            return

        decoded = packet.get('decoded', {}) if isinstance(packet, dict) else {}
        raw_text = decoded.get('text')
        raw_payload = decoded.get('payload')

        try:
            text = raw_text
            # payload = SysWrapper.deserialize(raw_payload)
            payload = raw_payload
        except Exception as e:
            print(f"❌ 反序列化失败: {e}")
            print(f"raw_payload: {type(raw_payload)}")
            return

        print(f"📩 [{getattr(self.interface, 'devPath', '<iface>')}] "
              f"from={packet.get('from')} to={packet.get('to')} text={text} payload={payload}")

        if payload:
            # self.queue.put(SysWrapper.to_json(payload))
            self.queue.put(payload)

    def receive_message(self):
        return self.queue.get()

    def listen_forever(self):
        print(f"开始监听接口 {getattr(self.interface, 'devPath', '<iface>')} ...")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"退出监听 {getattr(self.interface, 'devPath', '<iface>')}")
            self.interface.close()

    def close(self):
        self.interface.close()