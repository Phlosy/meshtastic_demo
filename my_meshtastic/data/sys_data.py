# sys_wrapper.py
import time
import json
from my_meshtastic.proto import GeoPoint, OtherUAVState, UAVData
from google.protobuf.json_format import Parse
import random

class SysWrapper:
    @staticmethod
    def generate_geo_point(lat=39.98, lon=116.3, alt=100.0) -> GeoPoint:
        """生成一个示例 GeoPoint"""
        return GeoPoint(
            latitude=int(lat * 1e7),
            longitude=int(lon * 1e7),
            altitude_msl=alt,
        )

    @staticmethod
    def generate_other_uav(uav_id=2) -> OtherUAVState:
        """生成一个示例 OtherUAVState"""
        return OtherUAVState(
            uav_id=uav_id,
            position=SysWrapper.generate_geo_point(lat=39.99, lon=116.31, alt=120.0),
            velocity_ned=[0.0, 5.0, -1.0],
        )

    @staticmethod
    def generate_data_demo(num=2) -> UAVData:
        """生成一条 UAVData 示例"""
        return UAVData(
            timestamp_us=int(time.time() * 1e6),
            uav_id=1,
            safe_space_min=SysWrapper.generate_geo_point(39.97+random.uniform(-0.1, 0.1), 116.29+random.uniform(-0.1, 0.1), 90.0+random.uniform(-10.0, 10.0)),
            safe_space_max=SysWrapper.generate_geo_point(39.99+random.uniform(-0.1, 0.1), 116.31+random.uniform(-0.1, 0.1), 110.0+random.uniform(-10.0, 10.0)),
            guidance_waypoint=SysWrapper.generate_geo_point(40.0+random.uniform(-0.1, 0.1), 116.32+random.uniform(-0.1, 0.1), 150.0+random.uniform(-10.0, 10.0)),
            expire_at_us=int(time.time() * 1e6) + 10_000_000,  # +10s
            traffic_count=num,
            traffic_data=[SysWrapper.generate_other_uav(i + 2) for i in range(num)],
        )

    @staticmethod
    def serialize(data: UAVData) -> bytes:
        """序列化为字节"""
        if data is None:
            return b""

        if hasattr(data, "SerializeToString"):
            return data.SerializeToString()

        if isinstance(data, str):
            msg = UAVData()
            Parse(data, msg, ignore_unknown_fields=True)
            return msg
        
        print(f"❌ 序列化失败：无法处理类型: {type(data)}")
        return None


    @staticmethod
    def deserialize(raw: bytes) -> UAVData:
        """反序列化为 UAVData"""
        msg = UAVData()

        if isinstance(raw, (bytes, bytearray)):
            try:
                msg.ParseFromString(raw)
                return msg
            except Exception as e:
                print(f"❌ 反序列化失败：无法处理类型: {type(raw)}")
                return None


    @staticmethod
    def to_json(data: UAVData) -> str:
        """转 JSON（便于调试/日志）"""
        return json.dumps(
            {
                "timestamp_us": data.timestamp_us,
                "uav_id": data.uav_id,
                "safe_space_min": {
                    "lat": data.safe_space_min.latitude,
                    "lon": data.safe_space_min.longitude,
                    "alt": data.safe_space_min.altitude_msl,
                },
                "safe_space_max": {
                    "lat": data.safe_space_max.latitude,
                    "lon": data.safe_space_max.longitude,
                    "alt": data.safe_space_max.altitude_msl,
                },
                "guidance_waypoint": {
                    "lat": data.guidance_waypoint.latitude,
                    "lon": data.guidance_waypoint.longitude,
                    "alt": data.guidance_waypoint.altitude_msl,
                },
                "expire_at_us": data.expire_at_us,
                "traffic_count": data.traffic_count,
                "traffic_data": [
                    {
                        "uav_id": f.uav_id,
                        "position": {
                            "lat": f.position.latitude,
                            "lon": f.position.longitude,
                            "alt": f.position.altitude_msl,
                        },
                        "velocity_ned": list(f.velocity_ned),
                    }
                    for f in data.traffic_data
                ],
            },
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def from_json(json_str: str) -> UAVData:
        """从 JSON 字符串还原为 UAVData"""
        obj = json.loads(json_str)

        def pos(d):
            return GeoPoint(
                latitude=d["lat"],
                longitude=d["lon"],
                altitude_msl=d["alt"],
            )

        traffic_list = [
            OtherUAVState(
                uav_id=f["uav_id"],
                position=pos(f["position"]),
                velocity_ned=tuple(f["velocity_ned"]),
            )
            for f in obj["traffic_data"]
        ]

        return UAVData(
            timestamp_us=obj["timestamp_us"],
            uav_id=obj["uav_id"],
            safe_space_min=pos(obj["safe_space_min"]),
            safe_space_max=pos(obj["safe_space_max"]),
            guidance_waypoint=pos(obj["guidance_waypoint"]),
            expire_at_us=obj["expire_at_us"],
            traffic_count=obj["traffic_count"],
            traffic_data=traffic_list,
        )