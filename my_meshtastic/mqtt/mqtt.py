import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, broker: str, port: int, topic: str):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

        # 绑定回调
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """连接成功回调"""
        if rc == 0:
            print(f"✅ 已连接到 MQTT Broker {self.broker}:{self.port}")
            # 自动订阅主题
            client.subscribe(self.topic)
            print(f"📩 已订阅主题: {self.topic}")
        else:
            print(f"❌ 连接失败, 返回码: {rc}")

    def on_message(self, client, userdata, msg):
        """收到消息回调"""
        print(f"📨 收到消息: {msg.topic} -> {msg.payload.decode()}")

    def connect(self):
        """连接到 Broker"""
        self.client.connect(self.broker, self.port, 60)

    def publish(self, message: str):
        """发布消息"""
        result = self.client.publish(self.topic, message)
        status = result[0]
        if status == 0:
            print(f"✅ 已发送消息到 {self.topic}: {message}")
        else:
            print(f"❌ 发送失败: {message}")

    def loop_forever(self):
        """保持连接并监听消息"""
        self.client.loop_forever()


if __name__ == "__main__":
    # 初始化客户端
    mqtt_client = MQTTClient(broker="localhost", port=1883, topic="test/topic")

    # 连接到 broker
    mqtt_client.connect()

    # 发布一条测试消息
    mqtt_client.publish("Hello from class wrapper!")

    # 进入循环，保持监听
    mqtt_client.loop_forever()
