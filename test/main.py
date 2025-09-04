import meshtastic
import meshtastic.serial_interface
from pubsub import pub

TARGET_NODE = "!c1107116"   # 👈 改成你要检查的节点ID

def check_direct_connection(interface, target_node):
    nodes = interface.nodes
    my_id = interface.myInfo.my_node_num

    print(f"本地节点: {hex(my_id)}")
    print("正在检查目标节点:", target_node)

    for node_id, node_info in nodes.items():
        if node_info.get("user") is None:
            continue

        if node_info["user"]["id"] == target_node:
            print(f"找到目标节点: {node_info['user']['longName']} ({target_node})")

            # 判断是否直连
            snr = node_info.get("snr")
            rssi = node_info.get("rssi")
            hops = node_info.get("hops")

            if snr is not None or rssi is not None:
                print(f"✅ 直连: RSSI={rssi}, SNR={snr}")
            elif hops and hops > 0:
                print(f"🔁 通过中继 (hops={hops})")
            else:
                print("❓ 无法判断，可能还没收到目标节点的数据")

            return

    print("❌ 没找到目标节点")

def main():
    interface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")  # 改成你的端口
    check_direct_connection(interface, TARGET_NODE)
    interface.close()

if __name__ == "__main__":
    main()
