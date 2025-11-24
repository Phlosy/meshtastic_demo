import meshtastic
import meshtastic.serial_interface

# 例如：连接到串口 /dev/ttyUSB0（请根据你的设备修改）
iface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM2")

iface.waitForConfig()  # 等待接口配置
node = iface.localNode
node.waitForConfig(attribute="channels")  # 等待频道配置被读取

url = node.getURL(includeAll=True)
print("Channel URL:", url)

iface.close()
