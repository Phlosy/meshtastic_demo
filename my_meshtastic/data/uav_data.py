# uav_wrapper.py
from my_meshtastic.proto import UAVStatus, UAVData
import time
import json

class UAVWrapper:
    @staticmethod
    def generate_status_demo() -> UAVStatus:
        """生成一条 UAVStatus 示例"""
        return UAVStatus(
            timestamp_us=int(time.time() * 1e6),
            uav_id=1,
            latitude=int(39.98 * 1e7),
            longitude=int(116.3 * 1e7),
            altitude_msl=100.0,
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
    def serialize(data: UAVData) -> bytes:
        """序列化为字节"""
        return data.SerializeToString()

    @staticmethod
    def deserialize(raw: bytes) -> UAVData:
        """从字节反序列化"""
        msg = UAVData()
        msg.ParseFromString(raw)
        return msg

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
