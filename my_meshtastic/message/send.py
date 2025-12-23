import meshtastic
import meshtastic.serial_interface
from pubsub import pub

# ------------------- 接口专属消息发送器 -------------------
# ------------------向mesh设备发送消息---------------------

class SysInterfaceSender:
    def __init__(self, interface: meshtastic.serial_interface.SerialInterface, sys_client):
        self.interface= interface
        self.sys_client = sys_client
        print(f"✅ 已绑定接口 {getattr(self.interface, 'devPath', '<iface>')}")

    def send_payload(self, data_message, target_node_id):
        """
        发送消息
        """
        target_node_id = target_node_id  # None 表示广播给所有节点
        data_message = data_message
        self.interface.sendData(data_message, destinationId=target_node_id)

        # print(f"Sent message: '{data_message}' to node {target_node_id}")

    def close(self):
        self.interface.close()

class UavInterfaceSender:
    def __init__(self, interface: meshtastic.serial_interface.SerialInterface):
        self.interface = interface
        print(f"✅ 已绑定接口 {getattr(self.interface, 'devPath', '<iface>')}")

    def send_payload(self, data_message, target_node_id):
        """
        发送消息
        """
        target_node_id = target_node_id  # None 表示广播给所有节点
        data_message = data_message
        self.interface.sendData(data_message, destinationId=target_node_id)

        # print(f"Sent message: '{data_message}' to node {target_node_id}")

    def close(self):
        self.interface.close()