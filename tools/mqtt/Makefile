# MQTT Docker Compose Makefile

# 默认目标
.PHONY: help up down clean clean-data clean-logs clean-all

help:
	@echo "可用的命令："
	@echo "  up        - 启动 MQTT 服务"
	@echo "  down      - 停止 MQTT 服务"
	@echo "  clean     - 停止服务并清理容器"
	@echo "  clean-data - 清理数据目录"
	@echo "  clean-logs - 清理日志目录"
	@echo "  clean-all - 清理所有数据、日志和容器"
	@echo "  status    - 查看服务状态"

# 启动 MQTT 服务
up:
	docker-compose up -d
	@echo "MQTT 服务已启动"

# 停止 MQTT 服务
down:
	docker-compose down
	@echo "MQTT 服务已停止"

# 停止服务并清理容器
clean:
	docker-compose down --remove-orphans
	docker-compose rm -f
	@echo "容器已清理"

# 清理数据目录
clean-data:
	@if [ -d "./data" ]; then \
		echo "清理数据目录..."; \
		sudo rm -rf ./data/*; \
		echo "数据目录已清理"; \
	else \
		echo "数据目录不存在"; \
	fi

# 清理日志目录
clean-logs:
	@if [ -d "./logs" ]; then \
		echo "清理日志目录..."; \
		sudo rm -rf ./logs/*; \
		echo "日志目录已清理"; \
	else \
		echo "日志目录不存在"; \
	fi

# 清理所有数据、日志和容器
clean-all: down clean clean-data clean-logs
	@echo "所有数据、日志和容器已清理"

# 查看服务状态
status:
	docker-compose ps

# 查看日志
logs:
	docker-compose logs -f

# 重启服务
restart: down up
	@echo "服务已重启"
