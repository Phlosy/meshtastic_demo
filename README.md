# Meshtastic Python 客户端

这是一个基于 Python 的 Meshtastic 客户端实现，用于与 Meshtastic 网络进行通信。

## 功能特性

- 连接到 Meshtastic 设备
- 发送和接收消息
- 节点管理
- 网络状态监控

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python pkg/cmd/main.py
```

## 配置

配置文件位于 `config/` 目录中。

在 Windows 中，直接用 COM3 或者 COM4 这样的字符串即可
例如 Python meshtastic.serial_interface.SerialInterface 初始化时：

import meshtastic.serial_interface

### Linux 写法
```
iface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")
```

### Windows 写法
```
iface = meshtastic.serial_interface.SerialInterface(devPath="COM3")
```

### 注意事项

COM1–COM9 可以直接写 "COM3"。

大于 COM9 的串口，需要用特殊格式写："\\\\.\\COM10"
例如：
```
iface = meshtastic.serial_interface.SerialInterface(devPath="\\\\.\\COM12")
```

建议在 Windows 上通过 mode 命令行确认可用串口：
```
mode
```

会列出所有串口设备。


