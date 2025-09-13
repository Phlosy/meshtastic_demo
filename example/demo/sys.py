import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.data import UavData

def main():
    # 加载配置
    devinfo=load_config("config/config.yaml")
    print(devinfo)

    # 生成UAV状态数据demo
    uav_data = UavData.generate_uav_data_demo(3)
    print(uav_data)

    


if __name__ == "__main__":
    main()