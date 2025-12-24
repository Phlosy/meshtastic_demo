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

# 接口断开后的重连间隔（秒），可根据需要调整
RECONNECT_INTERVAL_SECONDS = 5

# 健康检查间隔（秒），定期检查接口是否断开
HEALTH_CHECK_INTERVAL_SECONDS = 3


def _create_interface(uav_id, num_interfaces):
    """
    创建 Meshtastic 接口以及收发器
    
    Returns:
        tuple: (interface, uav_interface_receiver, uav_interface_sender, sys_id, dev_path)
    """
    # ---------------------------------------------- 加载配置 ----------------------------------------------
    devinfo = load_config("config/config.yaml")

    # 获取本地设备路径
    local_dev_path = []
    for i in range(num_interfaces):
        local_dev_path.append(devinfo["dev_path"]["dev" + str(i + 1)])

    # 获取连接的 uav/sys 设备ID
    uav_ids = []
    sys_ids = []
    for i in range(num_interfaces):
        uav_ids.append(devinfo["dev_id"]["uav" + str(i + 1)])
        sys_ids.append(devinfo["dev_id"]["hub" + str(i + 1)])

    print(local_dev_path, "\n")
    print(uav_ids, "\n")
    print(sys_ids, "\n")

    print(f"⚙️ 计划创建 uav{uav_id} Meshtastic 接口\n")

    # 创建meshtastic接口
    dev_path = local_dev_path[uav_id - 1]
    interface = meshtastic.serial_interface.SerialInterface(devPath=dev_path)

    uav_interface_receiver = UavInterfaceReceiver(interface)
    uav_interface_sender = UavInterfaceSender(interface)

    # 返回接口及 sys_id、dev_path，便于后续发送和健康检查使用
    return interface, uav_interface_receiver, uav_interface_sender, sys_ids[uav_id - 1], dev_path


def health_check_monitor(dev_path, interface, reconnect_event, check_interval):
    """
    健康检查监控线程：定期检查接口是否断开
    
    Args:
        dev_path: 串口设备路径（如 /dev/ttyUSB0）
        interface: Meshtastic 接口对象
        reconnect_event: 重连事件，检测到断开时设置
        check_interval: 检查间隔（秒）
    """
    logger.info(f"健康检查线程已启动，检查间隔: {check_interval}秒")
    
    while not reconnect_event.is_set():
        try:
            # 检查1: 串口设备文件是否存在
            if not os.path.exists(dev_path):
                logger.warning(f"❌ 串口设备文件不存在: {dev_path}，触发重连")
                reconnect_event.set()
                break
            
            # 检查2: 尝试访问接口属性，如果接口断开可能会失败
            try:
                # 尝试访问接口的一些基本属性
                _ = getattr(interface, 'devPath', None)
                # 如果接口有 noProto 属性，也尝试访问
                if hasattr(interface, 'noProto'):
                    _ = interface.noProto
            except (AttributeError, OSError, IOError) as e:
                logger.warning(f"❌ 无法访问接口属性，可能已断开: {e}，触发重连")
                reconnect_event.set()
                break
            except Exception as e:
                # 其他异常也视为可能断开
                logger.warning(f"❌ 接口健康检查异常: {e}，触发重连")
                reconnect_event.set()
                break
            
            # 检查通过，等待下次检查
            time.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"健康检查线程异常: {e}")
            reconnect_event.set()
            break


def main(uav_id, num_interfaces):
    """
    主入口：负责维护接口与 gRPC 的生命周期，并在断连时自动重连
    """
    while True:
        interface = None
        uav_interface_receiver = None
        uav_interface_sender = None
        uav_client = None
        spawned_threads = []
        reconnect_event = threading.Event()

        try:
            # 创建本地 Meshtastic 接口
            interface, uav_interface_receiver, uav_interface_sender, sys_id, dev_path = _create_interface(
                uav_id, num_interfaces
            )

            # 启动gRPC客户端
            uav_client = UavServiceClient(server_address="localhost:50052")
            if not uav_client.connect():
                print("无法连接到服务器，请确保服务器正在运行")
                raise RuntimeError("gRPC 服务器连接失败")

            # 启动健康检查线程（主动监测接口断开）
            t_health = threading.Thread(
                target=health_check_monitor,
                args=(dev_path, interface, reconnect_event, HEALTH_CHECK_INTERVAL_SECONDS),
                daemon=True,
            )
            t_health.start()
            spawned_threads.append(t_health)
            logger.info(f"健康检查线程已启动，监控设备: {dev_path}")

            # 接收线程
            t_recv = threading.Thread(
                target=uav_receive,
                args=(uav_interface_receiver, str(uav_id), uav_client, reconnect_event),
                daemon=True,
            )
            t_recv.start()
            spawned_threads.append(t_recv)

            # 启动gRPC服务器
            # 创建发送回调函数，当 gRPC 服务器接收到数据时触发
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
                        uav_send(uav_interface_sender, sys_id, uav_data, reconnect_event)
                    else:
                        uav_send(uav_interface_sender, sys_id, received_data, reconnect_event)
                except Exception as e:
                    logger.error(f"反序列化或发送数据失败: {e}")
                    # 出现异常时触发重连
                    reconnect_event.set()

            # 启动 gRPC 服务器（在单独的线程中）
            grpc_port = 50051  # 为每个 UAV 分配不同的端口
            t_grpc = threading.Thread(
                target=serve, args=(grpc_port,), kwargs={"send_callback": send_callback}, daemon=True
            )
            t_grpc.start()
            spawned_threads.append(t_grpc)

            logger.info(f"UAV {uav_id} 已启动，gRPC 服务器监听端口: {grpc_port}")
            logger.info("等待 gRPC 请求触发发送...")

            # 主线程阻塞等待重连事件或键盘中断
            while not reconnect_event.is_set():
                time.sleep(1)

            logger.warning("检测到接口断开或异常，准备重连 Meshtastic 接口...")

        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
            break
        except Exception as e:
            logger.error(f"主循环中发生异常，将在 {RECONNECT_INTERVAL_SECONDS}s 后重试: {e}")

        # 清理资源
        try:
            if uav_client is not None:
                uav_client.disconnect()
        except Exception:
            pass

        try:
            if interface is not None:
                # 根据 meshtastic 库实现，可能有 close/disconnect 等方法，这里做一次容错调用
                close_fn = getattr(interface, "close", None) or getattr(
                    interface, "disconnect", None
                )
                if callable(close_fn):
                    close_fn()
        except Exception:
            pass

        # 简单等待后重连
        logger.info(f"{RECONNECT_INTERVAL_SECONDS}s 后尝试重新连接接口...")
        time.sleep(RECONNECT_INTERVAL_SECONDS)

   

def uav_send(uav_interface_sender, sys_id, uav_data, reconnect_event=None):
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
    try:
        uav_interface_sender.send_payload(data, sys_id)
    except Exception as e:
        logger.error(f"发送数据到 sys_id={sys_id} 失败: {e}")
        if reconnect_event is not None:
            reconnect_event.set()


def uav_receive(uav_interface_receiver, uav_id, uav_client, reconnect_event=None):
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

            # 如果外部已经请求重连，则退出循环
            if reconnect_event is not None and reconnect_event.is_set():
                break

    except Exception as e:
        print(f"❌ uav_receive 出错: {e}\n")
        if reconnect_event is not None:
            reconnect_event.set()

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