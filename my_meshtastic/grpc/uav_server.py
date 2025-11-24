#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gRPC 服务端示例
演示如何使用生成的 protobuf 和 gRPC 代码实现服务端
"""

import grpc
from concurrent import futures
import logging

from my_meshtastic.grpc import uav_service_pb2
from my_meshtastic.grpc import uav_service_pb2_grpc

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UavServiceServicer(uav_service_pb2_grpc.UavServiceServicer):
    """实现 UavService 服务接口"""
    
    def __init__(self, send_callback=None):
        """
        初始化服务
        
        Args:
            send_callback: 可选的回调函数，当接收到 UploadStatus 请求时调用
                          回调函数签名: callback(request)
                          request 包含 uav_id 和 data 字段
        """
        self.send_callback = send_callback
    
    def UploadStatus(self, request, context):
        """
        处理上传无人机状态数据的请求
        
        Args:
            request: UploadStatusRequest 消息
            context: gRPC 上下文
            
        Returns:
            UploadStatusResponse 消息
        """
        logger.info(f"收到上传状态请求 - UAV ID: {request.uav_id}, 数据长度: {len(request.data)} 字节")
        
        # 在这里添加你的业务逻辑
        # 例如：验证数据、保存到数据库、处理状态信息等
        try:
            # 示例：简单的数据验证
            if not request.uav_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("uav_id 不能为空")
                return uav_service_pb2.UploadStatusResponse(
                    success=False,
                    message="uav_id 不能为空"
                )
            
            if not request.data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("data 不能为空")
                return uav_service_pb2.UploadStatusResponse(
                    success=False,
                    message="data 不能为空"
                )
            
            # 如果设置了回调函数，则调用它来触发发送，传入请求数据
            if self.send_callback is not None:
                try:
                    logger.info("触发发送回调函数")
                    self.send_callback(request)
                except Exception as callback_error:
                    logger.error(f"调用发送回调函数时出错: {callback_error}")
            
            # TODO: 在这里添加你的业务逻辑
            # 例如：
            # - 解析和验证数据
            # - 保存到数据库
            # - 更新无人机状态
            # - 触发其他服务
            
            logger.info(f"成功处理 UAV {request.uav_id} 的状态数据")
            
            return uav_service_pb2.UploadStatusResponse(
                success=True,
                message=f"成功接收 UAV {request.uav_id} 的状态数据，数据大小: {len(request.data)} 字节"
            )
            
        except Exception as e:
            logger.error(f"处理上传状态请求时出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return uav_service_pb2.UploadStatusResponse(
                success=False,
                message=f"服务器错误: {str(e)}"
            )
    
    def SetSafetySpace(self, request, context):
        """
        处理下发无人机安全空间的请求
        
        Args:
            request: SetSafetySpaceRequest 消息
            context: gRPC 上下文
            
        Returns:
            SetSafetySpaceResponse 消息
        """
        logger.info(f"收到设置安全空间请求 - UAV ID: {request.uav_id}, 数据长度: {len(request.data)} 字节")
        
        # 在这里添加你的业务逻辑
        # 例如：验证安全空间数据、下发到无人机、更新配置等
        try:
            # 示例：简单的数据验证
            if not request.uav_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("uav_id 不能为空")
                return uav_service_pb2.SetSafetySpaceResponse(
                    success=False,
                    message="uav_id 不能为空"
                )
            
            if not request.data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("data 不能为空")
                return uav_service_pb2.SetSafetySpaceResponse(
                    success=False,
                    message="data 不能为空"
                )
            
            # TODO: 在这里添加你的业务逻辑
            # 例如：
            # - 解析和验证安全空间数据
            # - 检查权限
            # - 下发到无人机
            # - 更新配置数据库
            # - 通知相关服务
            
            logger.info(f"成功为 UAV {request.uav_id} 设置安全空间")
            
            return uav_service_pb2.SetSafetySpaceResponse(
                success=True,
                message=f"成功为 UAV {request.uav_id} 设置安全空间，数据大小: {len(request.data)} 字节"
            )
            
        except Exception as e:
            logger.error(f"处理设置安全空间请求时出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return uav_service_pb2.SetSafetySpaceResponse(
                success=False,
                message=f"服务器错误: {str(e)}"
            )


def serve(port=50051, send_callback=None):
    """
    启动 gRPC 服务器
    
    Args:
        port: 服务器监听端口，默认 50051
        send_callback: 可选的回调函数，当接收到 UploadStatus 请求时调用
    """
    # 创建 gRPC 服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 注册服务
    uav_service_pb2_grpc.add_UavServiceServicer_to_server(
        UavServiceServicer(send_callback=send_callback), server
    )
    
    # 监听端口
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    # 启动服务器
    server.start()
    logger.info(f"gRPC 服务器已启动，监听端口: {port}")
    logger.info(f"服务器地址: {listen_addr}")
    
    try:
        # 保持服务器运行
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务器...")
        server.stop(0)
        logger.info("服务器已关闭")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='UAV gRPC 服务端')
    parser.add_argument(
        '--port',
        type=int,
        default=50051,
        help='服务器监听端口 (默认: 50051)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("UAV gRPC 服务端")
    print("=" * 60)
    print(f"监听端口: {args.port}")
    print("=" * 60)
    print()
    
    serve(port=args.port)

