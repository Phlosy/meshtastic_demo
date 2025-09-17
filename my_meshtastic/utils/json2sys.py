import json
from my_meshtastic.proto.sysstatus_pb2 import UAVData, GeoPoint, OtherUAVState
from my_meshtastic.data.sys_data import SysWrapper  # 如果用我之前写的辅助类


def json_to_uavdata(json_str: str) -> UAVData:
    """从 JSON 字符串解析为 UAVData"""
    data_dict = json.loads(json_str)
    uav = UAVData()

    # 基本字段
    uav.timestamp_us = data_dict["timestamp_us"]
    uav.uav_id = data_dict["uav_id"]
    uav.expire_at_us = data_dict["expire_at_us"]
    uav.traffic_count = data_dict["traffic_count"]

    # safe_space_min
    uav.safe_space_min.CopyFrom(
        GeoPoint(
            latitude=data_dict["safe_space_min"]["lat"],
            longitude=data_dict["safe_space_min"]["lon"],
            altitude_msl=data_dict["safe_space_min"]["alt"],
        )
    )

    # safe_space_max
    uav.safe_space_max.CopyFrom(
        GeoPoint(
            latitude=data_dict["safe_space_max"]["lat"],
            longitude=data_dict["safe_space_max"]["lon"],
            altitude_msl=data_dict["safe_space_max"]["alt"],
        )
    )

    # guidance_waypoint
    uav.guidance_waypoint.CopyFrom(
        GeoPoint(
            latitude=data_dict["guidance_waypoint"]["lat"],
            longitude=data_dict["guidance_waypoint"]["lon"],
            altitude_msl=data_dict["guidance_waypoint"]["alt"],
        )
    )

    # traffic_data
    for t in data_dict["traffic_data"]:
        other = OtherUAVState(
            uav_id=t["uav_id"],
            position=GeoPoint(
                latitude=t["position"]["lat"],
                longitude=t["position"]["lon"],
                altitude_msl=t["position"]["alt"],
            ),
            velocity_ned=t["velocity_ned"],
        )
        uav.traffic_data.append(other)

    return uav


def serialize_for_mqtt(json_str: str) -> bytes:
    """从 JSON 转换为 Protobuf 并序列化成字节"""
    uav_msg = json_to_uavdata(json_str)
    return uav_msg.SerializeToString()


def deserialize_from_mqtt(raw: bytes) -> str:
    """从字节反序列化 UAVData 并转 JSON"""
    msg = UAVData()
    msg.ParseFromString(raw)
    return SysWrapper.to_json(msg)  # 用之前的 to_json 美化输出


# ================= 用法演示 =================
if __name__ == "__main__":
    # 模拟 MQTT 收到 JSON
    json_demo = json.dumps(SysWrapper.generate_data_demo(2).to_dict())  # 假设你转成 dict

    # JSON → Protobuf → 序列化
    raw_bytes = serialize_for_mqtt(json_demo)

    # 再还原回来看看
    restored_json = deserialize_from_mqtt(raw_bytes)

    print("原始 JSON:\n", json_demo)
    print("序列化长度:", len(raw_bytes))
    print("还原 JSON:\n", restored_json)
