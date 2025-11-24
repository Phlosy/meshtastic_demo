#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gRPC 客户端示例
演示如何使用生成的 protobuf 和 gRPC 代码实现客户端
"""

import sys
import os
import grpc
import logging

from my_meshtastic.grpc import uav_service_pb2
from my_meshtastic.grpc import uav_service_pb2_grpc

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UavServiceClient:
    """UAV 服务客户端"""
    
    def __init__(self, server_address='localhost:50051'):
        """
        初始化客户端
        
        Args:
            server_address: 服务器地址，格式: 'host:port'
        """
        self.server_address = server_address
        self.channel = None
        self.stub = None
    
    def connect(self):
        """连接到服务器"""
        try:
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = uav_service_pb2_grpc.UavServiceStub(self.channel)
            logger.info(f"已连接到服务器: {self.server_address}")
            
            # 测试连接
            grpc.channel_ready_future(self.channel).result(timeout=5)
            logger.info("连接测试成功")
            return True
        except grpc.FutureTimeoutError:
            logger.error(f"连接超时: 无法连接到服务器 {self.server_address}")
            return False
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.channel:
            self.channel.close()
            logger.info("已断开连接")
    
    def upload_status(self, uav_id, data):
        """
        上传无人机状态数据
        
        Args:
            uav_id: 无人机编号
            data: 字节流数据
            
        Returns:
            UploadStatusResponse 消息，如果出错返回 None
        """
        if not self.stub:
            logger.error("未连接到服务器，请先调用 connect()")
            return None
        
        try:
            # 创建请求
            request = uav_service_pb2.UploadStatusRequest()
            request.uav_id = uav_id
            request.data = data if isinstance(data, bytes) else data.encode('utf-8')
            
            logger.info(f"发送上传状态请求 - UAV ID: {uav_id}, 数据长度: {len(request.data)} 字节")
            
            # 调用 RPC
            response = self.stub.UploadStatus(request, timeout=10)
            
            logger.info(f"收到响应 - 成功: {response.success}, 消息: {response.message}")
            return response
            
        except grpc.RpcError as e:
            logger.error(f"RPC 调用失败: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            logger.error(f"上传状态时出错: {e}")
            return None
    
    def set_safety_space(self, uav_id, data):
        """
        设置无人机安全空间
        
        Args:
            uav_id: 无人机编号
            data: 字节流数据
            
        Returns:
            SetSafetySpaceResponse 消息，如果出错返回 None
        """
        if not self.stub:
            logger.error("未连接到服务器，请先调用 connect()")
            return None
        
        try:
            # 创建请求
            request = uav_service_pb2.SetSafetySpaceRequest()
            request.uav_id = uav_id
            request.data = data if isinstance(data, bytes) else data.encode('utf-8')
            
            logger.info(f"发送设置安全空间请求 - UAV ID: {uav_id}, 数据长度: {len(request.data)} 字节")
            
            # 调用 RPC
            response = self.stub.SetSafetySpace(request, timeout=10)
            
            logger.info(f"收到响应 - 成功: {response.success}, 消息: {response.message}")
            return response
            
        except grpc.RpcError as e:
            logger.error(f"RPC 调用失败: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            logger.error(f"设置安全空间时出错: {e}")
            return None


def main():
    """主函数 - 演示客户端使用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UAV gRPC 客户端')
    parser.add_argument(
        '--server',
        type=str,
        default='localhost:50051',
        help='服务器地址 (默认: localhost:50051)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='运行测试示例'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("UAV gRPC 客户端")
    print("=" * 60)
    print(f"服务器地址: {args.server}")
    print("=" * 60)
    print()
    
    # 创建客户端
    client = UavServiceClient(server_address=args.server)
    
    # 连接到服务器
    if not client.connect():
        print("无法连接到服务器，请确保服务器正在运行")
        return
    
    try:
        if args.test:
            # 运行测试示例
            print("\n[测试 1] 上传无人机状态数据")
            print("-" * 60)
            response = client.upload_status(
                uav_id="UAV-001",
                data=b"status_data_12345"
            )
            if response:
                print(f"✓ 成功: {response.message}")
            else:
                print("✗ 失败")
            
            print("\n[测试 2] 设置无人机安全空间")
            print("-" * 60)
            response = client.set_safety_space(
                uav_id="UAV-001",
                data=b"safety_space_config_data"
            )
            if response:
                print(f"✓ 成功: {response.message}")
            else:
                print("✗ 失败")
            
            print("\n[测试 3] 测试错误处理 - 空 uav_id")
            print("-" * 60)
            response = client.upload_status(
                uav_id="",
                data=b"test_data"
            )
            if response:
                print(f"响应: {response.message}")
            else:
                print("✗ 请求失败")
        else:
            # 交互模式
            print("\n交互模式 (输入 'quit' 退出)")
            print("可用命令:")
            print("  upload <uav_id> <data>  - 上传状态数据")
            print("  safety <uav_id> <data>  - 设置安全空间")
            print("  quit                    - 退出")
            print()
            
            while True:
                try:
                    cmd = input("> ").strip()
                    if not cmd or cmd == 'quit':
                        break
                    
                    parts = cmd.split(None, 2)
                    if len(parts) < 3:
                        print("错误: 命令格式不正确")
                        continue
                    
                    action, uav_id, data = parts
                    
                    if action == 'upload':
                        response = client.upload_status(uav_id, data.encode('utf-8'))
                        if response:
                            print(f"结果: {response.message}")
                    elif action == 'safety':
                        response = client.set_safety_space(uav_id, data.encode('utf-8'))
                        if response:
                            print(f"结果: {response.message}")
                    else:
                        print(f"未知命令: {action}")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"错误: {e}")
    
    finally:
        # 断开连接
        client.disconnect()
        print("\n客户端已关闭")


if __name__ == "__main__":
    main()

