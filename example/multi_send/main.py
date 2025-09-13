import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from my_meshtastic.loader import load_config
from my_meshtastic.message.send import send_message
from my_meshtastic.data import generate_150b_data
import time
import meshtastic
import meshtastic.serial_interface


def main():
    source_dev_list= ["dev1", "dev2"]
    devinfo=load_config("config/config.yaml")
    interface_list = []
    print(devinfo)
    for source_dev in source_dev_list:
        interface_list.append(meshtastic.serial_interface.SerialInterface(devPath=devinfo[source_dev]))

    for i in range(10):
        data = generate_150b_data()
        print("数据包大小为：" + str(len(data)) + "字节")
        j=1
        for interface in interface_list:
            send_message(interface, "from " + "dev"+ str(j) + " " + str(i) + ":" + data, devinfo['dev4_id'])
            j+=1
            time.sleep(4)

    for interface in interface_list:
        interface.close()

    #拆成5个包发送

    # for i in range(20):
    #     # send_message(interface, data_list[0], devinfo['dev4_id'])
    #     # send_message(interface, data_list[1], devinfo['dev4_id'])
    #     # send_message(interface, data_list[2], devinfo['dev4_id'])
    #     # send_message(interface, data_list[3], devinfo['dev4_id'])
    #     # send_message(interface, data_list[4], devinfo['dev4_id'])
    #     # send_message(interface, "hello" + str(i), devinfo['dev3_id'])
    #     send_message(interface, "from " + source_dev + " " + str(i) + ":" + data, devinfo['dev4_id'])
    #     time.sleep(4)
    # interface.close()
    


if __name__ == "__main__":
    main()