# sys_wrapper.py
import time
import json
from my_meshtastic.proto import GeoPoint, OtherUAVState, UAVData


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
            safe_space_min=SysWrapper.generate_geo_point(39.97, 116.29, 90.0),
            safe_space_max=SysWrapper.generate_geo_point(39.99, 116.31, 110.0),
            guidance_waypoint=SysWrapper.generate_geo_point(40.0, 116.32, 150.0),
            expire_at_us=int(time.time() * 1e6) + 10_000_000,  # +10s
            traffic_count=num,
            traffic_data=[SysWrapper.generate_other_uav(i + 2) for i in range(num)],
        )

    @staticmethod
    def serialize(data: UAVData) -> bytes:
        """序列化为字节"""
        return data.SerializeToString()

    @staticmethod
    def deserialize(raw: bytes) -> UAVData:
        """反序列化为 UAVData"""
        msg = UAVData()
        msg.ParseFromString(raw)
        return msg

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
