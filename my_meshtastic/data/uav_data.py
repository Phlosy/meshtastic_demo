# uav_wrapper.py
from google.protobuf.json_format import Parse
from my_meshtastic.proto.uavstatus_pb2 import UAVStatus, UAVData
import time
import json
import random

class UAVWrapper:
    @staticmethod
    def generate_status_demo() -> UAVStatus:
        """生成一条 UAVStatus 示例"""
         # 在 ±0.01 量级（即 ±0.01 度 ≈ ±1km）范围内增加随机扰动
        lat = 39.98 + random.uniform(-0.01, 0.01)
        lon = 116.3 + random.uniform(-0.01, 0.01)
        alt = 100.0 + random.uniform(-0.01, 0.01)  # 高度单位是米，这里相当于 ±1 cm 微扰

        return UAVStatus(
            timestamp_us=int(time.time() * 1e6),
            uav_id=1,
            latitude=int(lat * 1e7),
            longitude=int(lon * 1e7),
            altitude_msl=alt,
            attitude_q=[0.7071, 0.0, 0.0, 0.7071],
            velocity_ned=[0.0, 0.0, -1.0],
        )

    @staticmethod
    def generate_data_demo(num=1) -> UAVData:
        """生成一条 UAVData 示例"""
        return UAVData(
            type="record",
            name="UAVStatus",
            fields=[UAVWrapper.generate_status_demo() for _ in range(num)]
        )

    @staticmethod
    def serialize(data) -> bytes:
        """
        通用序列化函数：
        - UAVData 对象：调用 SerializeToString()
        - dict：转换为 UAVData 后再序列化
        - str：若能解析为 JSON 就转成 UAVData，否则按 UTF-8 文本编码
        - bytes：原样返回
        """
        if data is None:
            return b""

        # ✅ 已是 UAVData
        if hasattr(data, "SerializeToString"):
            return data.SerializeToString()

        if isinstance(data, str):
            msg = UAVData()
            Parse(data, msg, ignore_unknown_fields=True)
            return msg.SerializeToString()
        
        print(f"❌ 序列化失败：无法处理类型: {type(data)}")
        return None

    @staticmethod
    def deserialize(raw) -> UAVData:
        """
        通用反序列化：
        - bytes：ParseFromString()
        - str：尝试解析 JSON → UAVData
        - 其他类型：抛异常
        """
        msg = UAVData()

        # ✅ 如果是 protobuf bytes

        try:
            msg.ParseFromString(raw)
            return msg
        except Exception as e:
            raise ValueError(f"反序列化失败（非有效的UAVData字节流）: {e}")


    @staticmethod
    def to_json(data: UAVData) -> str:
        """转 JSON（便于调试/日志）"""
        return json.dumps(
            {
                "type": data.type,
                "name": data.name,
                "fields": [
                    {
                        "timestamp_us": f.timestamp_us,
                        "uav_id": f.uav_id,
                        "latitude": f.latitude,
                        "longitude": f.longitude,
                        "altitude_msl": f.altitude_msl,
                        "attitude_q": list(f.attitude_q),
                        "velocity_ned": list(f.velocity_ned),
                    }
                    for f in data.fields
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
