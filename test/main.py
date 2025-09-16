import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from my_meshtastic.proto import UAVStatus

# # 构建数据
# msg = UAVStatus(
#     timestamp_us=1726489200000000,
#     uav_id=1,
#     latitude=int(39.98 * 1e7),
#     longitude=int(116.3 * 1e7),
#     altitude_msl=100,
#     attitude_q=[0.7071, 0, 0, 0.7071],
#     velocity_ned=[0.0, 0.0, -1.0]
# )

# # 序列化
# data = msg.SerializeToString()
# print("字节大小:", len(data))

# # 反序列化
# msg2 = UAVStatus()
# msg2.ParseFromString(data)
# print("还原后的消息:", msg2)

from my_meshtastic.data import UavData
import json

uva_data = UavData.generate_uav_data_demo(2)
json_data = json.dumps(uva_data, ensure_ascii=False)
print(len(json_data))