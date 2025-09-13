from dataclasses import dataclass

@dataclass
class UavStatus:
    def __init__(
        self,
        timestamp_us: int,
        uav_id: int,
        latitude: int,
        longitude: int,
        altitude_msl: float,
        attitude_q: list,
        velocity_ned: list
    ):
        """
        :param timestamp_us: UNIX 时间戳 (微秒), uint64_t
        :param uav_id: 无人机唯一标识符, uint32_t
        :param latitude: WGS-84 坐标系, 整数格式: 度 * 1e7, int32_t
        :param longitude: WGS-84 坐标系, 整数格式: 度 * 1e7, int32_t
        :param altitude_msl: 相对于平均海平面 (MSL) 的高度，单位：米, float
        :param attitude_q: 姿态四元数 [w, x, y, z], float[4]
        :param velocity_ned: NED 坐标系下的速度矢量 [vx, vy, vz]，单位：米/秒, float[3]
        """
        self.timestamp_us = timestamp_us
        self.uav_id = uav_id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude_msl = altitude_msl
        if len(attitude_q) != 4:
            raise ValueError("attitude_q 必须为长度为4的列表 [w, x, y, z]")
        self.attitude_q = attitude_q
        if len(velocity_ned) != 3:
            raise ValueError("velocity_ned 必须为长度为3的列表 [vx, vy, vz]")
        self.velocity_ned = velocity_ned
    
    @staticmethod
    def generate_uav_data_demo() -> dict:
        timestamp_us = 1726339200000000
        uav_id = 1
        latitude = 39.980000000000004
        longitude = 116.30000000000001
        altitude_msl = 100
        attitude_q = [0.7071067811865476, 0, 0, 0.7071067811865476]
        velocity_ned = [0, 0, 0]
        
        # return {
        #     "timestamp_us": timestamp_us,
        #     "uav_id": uav_id,
        #     "latitude": latitude,
        #     "longitude": longitude,
        #     "altitude_msl": altitude_msl,
        #     "attitude_q": attitude_q,
        #     "velocity_ned": velocity_ned,
        # }

        return {
            "t": timestamp_us,
            "id": uav_id,
            "lat": latitude,
            "lon": longitude,
            "alt": altitude_msl,
            "q": attitude_q,
            "v": velocity_ned,
        }


@dataclass
class UavData:
    def __init__(
        self,
        type: str,
        name: str,
        fields: list[UavStatus]
    ):
        self.type = type
        self.name = name
        self.fields = fields
    
    # 生成UAV状态数据demo
    @staticmethod
    def generate_uav_data_demo(num: int) -> dict:
        type = "record"
        name = "UAVStatus"
        fields = []
        for i in range(num):
            fields.append(UavStatus.generate_uav_data_demo())
        # return {
        #     "type": type,
        #     "name": name,
        #     "fields": fields
        # }

        return {
            "t": type,
            "n": name,
            "f": fields
        }