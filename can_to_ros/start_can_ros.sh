#!/bin/bash
# ============================================
# CAN-to-ROS 2 一键启动脚本
# 用法：bash start_can_ros.sh
# ============================================

echo "========================================"
echo "  CAN-to-ROS2 数据转发节点 启动中..."
echo "========================================"

# 1. 加载虚拟 CAN 总线模块
echo "[1/4] 加载虚拟 CAN 总线模块..."
sudo modprobe can 2>/dev/null
sudo modprobe can_raw 2>/dev/null
sudo modprobe vcan 2>/dev/null

# 如果 vcan0 不存在，则创建
if ! ip link show vcan0 &>/dev/null; then
    sudo ip link add dev vcan0 type vcan
fi
sudo ip link set up vcan0
echo "  ✓ vcan0 已就绪"

# 2. 激活 Python 虚拟环境
echo "[2/4] 激活 Python 虚拟环境..."
source ~/can_ros_env/bin/activate
echo "  ✓ 虚拟环境已激活"

# 3. 加载 ROS 2 和工作空间环境
echo "[3/4] 加载 ROS 2 环境..."
source /opt/ros/jazzy/setup.bash
source ~/can_ros_ws/install/setup.bash
echo "  ✓ ROS 2 环境已加载"

# 4. 运行节点
echo "[4/4] 启动 CAN-to-ROS 2 节点..."
echo "========================================"
echo ""
echo "  提示：打开另一个终端运行测试发送："
echo "  while true; do cansend vcan0 100#006401F400000000; sleep 1; done"
echo ""
echo "  再打开第三个终端查看话题："
echo "  source /opt/ros/jazzy/setup.bash"
echo "  source ~/can_ros_ws/install/setup.bash"
echo "  ros2 topic echo /can_signals/enginespeed"
echo ""
echo "========================================"

python3 ~/can_ros_ws/src/can_to_ros/can_to_ros/can_to_ros_node.py \
    --ros-args \
    -p dbc_file:=/home/mrkedow/can_ros_ws/src/can_to_ros/example.dbc \
    -p can_interface:=vcan0