import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import meshtastic
import meshtastic.serial_interface
import threading
import time
import logging

from my_meshtastic.loader import load_config
from my_meshtastic.message.send import UavInterfaceSender
from my_meshtastic.message.receive import UavInterfaceReceiver
from my_meshtastic.data import UAVWrapper
from my_meshtastic.data import SysWrapper
from my_meshtastic.grpc.uav_server import serve
from my_meshtastic.grpc.uav_client import UavServiceClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(uav_id, num_interfaces):
 
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

    print(f"⚙️ 计划创建 uav{uav_id} Meshtastic 接口\n")

    spawned_threads = []

    # 创建meshtastic接口
    try:
        dev_path = local_dev_path[uav_id-1]
        interface = meshtastic.serial_interface.SerialInterface(devPath=dev_path)
    except Exception as e:
        print(f"❌ 创建 uav{uav_id} 接口失败: {e}\n")
        sys.exit(1)

    try:
        uav_interface_receiver = UavInterfaceReceiver(interface)
    except Exception as e:
        print(f"❌ 创建 uav{uav_id} 接口接收器失败: {e}\n")
        sys.exit(1)

    try:
        uav_interface_sender = UavInterfaceSender(interface)
    except Exception as e:
        print(f"❌ 创建 uav{uav_id} 接口发送器失败: {e}\n")
        sys.exit(1)

    # 启动gRPC客户端
    uav_client = UavServiceClient(server_address='localhost:50056')
    if not uav_client.connect():
        print("无法连接到服务器，请确保服务器正在运行")
        return

    t_recv = threading.Thread(
        target=uav_receive, args=(uav_interface_receiver, uav_id, uav_client), daemon=True
    )
    t_recv.start()
    spawned_threads.append(t_recv)

    # 启动gRPC服务器
    # 创建发送回调函数，当 gRPC 服务器接收到数据时触发
    sys_id = sys_ids[uav_id-1]
    def send_callback(request):
        """
        gRPC 接收到数据时触发的回调函数
        
        Args:
            request: UploadStatusRequest 消息，包含 uav_id 和 data 字段
        """
        # 从 gRPC 请求中提取数据
        received_uav_id = request.uav_id
        received_data = request.data
        
        # 将接收到的数据反序列化为 UAV 数据对象
        try:
            if type(received_data) != bytes:
                # uav_data = UAVWrapper.deserialize(received_data)
                uav_data = received_data
                logger.info(f"接收到 UAV {received_uav_id} 的数据，触发发送")
                uav_send(uav_interface_sender, sys_id, uav_data)
            else:
                uav_send(uav_interface_sender, sys_id, received_data)
        except Exception as e: 
            logger.error(f"反序列化数据失败: {e}")
            # 如果反序列化失败，可以尝试使用原始数据或其他处理方式
            uav_send(uav_interface_sender, sys_id, received_data)
    
    # 启动 gRPC 服务器（在单独的线程中）
    grpc_port = 50055  # 为每个 UAV 分配不同的端口
    t_grpc = threading.Thread(
        target=serve, args=(grpc_port,), kwargs={'send_callback': send_callback}, daemon=True
    )
    t_grpc.start()
    spawned_threads.append(t_grpc)
    
    logger.info(f"UAV {uav_id} 已启动，gRPC 服务器监听端口: {grpc_port}")
    logger.info("等待 gRPC 请求触发发送...")
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")

   

def uav_send(uav_interface_sender, sys_id, uav_data):
    """
    发送 UAV 数据到指定的 sys 设备
    
    Args:
        uav_interface_sender: Meshtastic 接口发送器
        sys_id: 目标 sys 设备 ID
        uav_data: UAV 数据对象（UAVData）
    """
    # print(f"准备发送 UAV 数据到 sys_id: {sys_id}")
    # print(f"UAV 数据: {uav_data}")

    # data = UAVWrapper.serialize(uav_data)
    data = uav_data
    # print(len(data))
    # 发送到sys上的设备
    uav_interface_sender.send_payload(data, sys_id)


def uav_receive(uav_interface_receiver, uav_id, uav_client):
    """
    从全局接收队列获取 Meshtastic 消息，打印
    """
    try:
        while True:
            msg = uav_interface_receiver.receive_message()  # 阻塞直到收到消息（listen 线程产出）

            if msg is None:
                time.sleep(0.05)
                continue

            # payload = SysWrapper.deserialize(msg)
            payload = msg
            print("📥 接收自 Meshtastic:", payload, "\n")
            print("payload type:", type(payload))

            # uav_client.upload_status(str(uav_id), payload)
            uav_client.set_safety_space(str(uav_id), payload)

    except Exception as e:
        print(f"❌ uav_receive 出错: {e}\n")

if __name__ == "__main__":
    uav_id = None
    num_interfaces = 4

    if len(sys.argv) ==2:
        uav_id = int(sys.argv[1])
    elif len(sys.argv) > 2:
        uav_id = int(sys.argv[1])
        num_interfaces = int(sys.argv[2])
    else:
        print("🔴 参数输入错误，请输入正确参数，例如：python uav.py 1 4\n")
        sys.exit(1)

    main(uav_id, num_interfaces)