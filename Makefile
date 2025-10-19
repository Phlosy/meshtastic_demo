# Meshtastic Demo Makefile

.PHONY: run-uav run-sys requirements install clean lint test

num_interfaces ?= 4

# 允许把多出来的“目标”（比如 1、2）当作位置参数吞掉，避免 "No rule to make target '1'"
%:
	@:

# 运行 SYS 节点（可选：位置参数1=接口数；或用 num_interfaces=N）
run-sys:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	num_interfaces_val="$${1:-$(num_interfaces)}"; \
	echo "⚙️ 启动 $$num_interfaces_val 个 Meshtastic 接口"; \
	python running/sys.py $$num_interfaces_val

# 运行 UAV 节点（位置参数1=uav_id，位置参数2=接口数；也兼容 uav_id= / num_interfaces=）
run-uav:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	uav_id_val="$${1:-$(uav_id)}"; \
	num_interfaces_val="$${2:-$(num_interfaces)}"; \
	if [ -z "$$uav_id_val" ]; then \
		echo "用法: make run-uav <uav_id> [num_interfaces] 例如: make run-uav 1 4"; \
		exit 1; \
	fi; \
	echo "🚀 启动 UAV $$uav_id_val，接口数 $$num_interfaces_val"; \
	python running/uav.py $$uav_id_val $$num_interfaces_val

# 生成依赖列表
requirements:
	pip freeze > requirements.txt

# 安装依赖
install:
	pip install -r requirements.txt

# 清理 pyc 和缓存
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 代码静态检查
lint:
	flake8 my_meshtastic/ running/ test/ example/

# 运行测试
test:
	pytest --maxfail=5 --disable-warnings

# 常用 demo 测试入口
demo-uav:
	python example/demo/uav.py

demo-sys:
	python example/demo/sys.py

# 运行 MQTT 测试
mqtt-send:
	python test/mqtt_send.py

mqtt-receive:
	python test/mqtt_receive.py

# 帮助
help:
	@echo "可用命令:"
	@echo "  make run-uav uav_id=<1~4> [num_interfaces=4] - 启动 UAV"
	@echo "  make run-sys [num_interfaces=4]              - 启动 SYS"
	@echo "  make install                                 - 安装依赖"
	@echo "  make requirements                            - 生成 requirements.txt"
	@echo "  make lint                                    - flake8 代码检查"
	@echo "  make test                                    - pytest 运行测试"
	@echo "  make clean                                   - 清理缓存"
	@echo "  make demo-uav / demo-sys                     - 运行 example 演示"
	@echo "  make mqtt-send / mqtt-receive                - MQTT demo"
	@echo "  make help                                    - 显示本帮助"
