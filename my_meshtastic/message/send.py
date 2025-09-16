import meshtastic
import meshtastic.serial_interface

def send_message(interface, data_message, target_node_id):
    """
    发送消息
    """
    # 1. 连接本地设备（串口或者 USB）
    # 如果设备是 USB 接口，类似 '/dev/ttyUSB0'
    # interface = meshtastic.serial_interface.SerialInterface(devPath=devPath)

    # 2. 获取目标节点的节点 ID 或者使用广播
    # 广播发送：destId = None
    # 单播发送：destId = '<节点的数字 ID>'
    target_node_id = target_node_id  # None 表示广播给所有节点

    # 3. 发送文本消息
    data_message = data_message

    interface.sendData(data_message, destinationId=target_node_id)

    print(f"Sent message: '{data_message}' to node {target_node_id}")

    # 4. 关闭接口
    # interface.close()
