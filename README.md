# CAN-to-ROS 2 总线数据转发节点

将 CAN 总线原始报文实时转换为 ROS 2 标准话题的 Python 节点。基于 SocketCAN 和 cantools，适用于将底层车载总线数据接入自动驾驶中间件的开发与测试场景。

## 功能

- 通过 SocketCAN 监听虚拟 CAN 总线（vcan0）上的原始报文
- 使用 DBC 文件解码报文中的物理信号（如发动机转速、车速）
- 将解码后的信号自动发布为 ROS 2 话题（`std_msgs/Float32`）
- 可以通过 ROS 2 参数配置 DBC 文件路径和 CAN 接口名称

## 依赖

- 操作系统：Ubuntu 24.04（或已启用 vcan 内核模块的 WSL2）
- ROS 2 发行版：Jazzy Jalisco
- Python 库：`cantools`、`python-can`
- 系统工具：`can-utils`

## 项目结构

```
can_to_ros/
├── can_to_ros/                  # Python 源码包
│   ├── __init__.py
│   └── can_to_ros_node.py       # ROS 2 节点主程序
├── resource/                    # 包资源
│   └── can_to_ros
├── package.xml                  # ROS 2 包描述文件
├── setup.py                     # 安装和入口点配置
├── setup.cfg
├── example.dbc                  # 示例 DBC 文件
└── README.md
```

## 安装与编译

### 1. 克隆仓库（或直接放入工作空间）

将 `can_to_ros` 文件夹放入你的 ROS 2 工作空间的 `src` 目录下：

```bash
cd ~/can_ros_ws/src
# 假设已将 can_to_ros 文件夹复制到此处
```

### 2. 安装 Python 依赖（venv）

```bash
python3 -m venv ~/can_ros_env
source ~/can_ros_env/bin/activate
pip install cantools python-can pyyaml setuptools
```

### 3. 编译工作空间

```bash
source /opt/ros/jazzy/setup.bash
cd ~/can_ros_ws
colcon build --symlink-install
source install/setup.bash
```

## 使用方法

### 第一步：启动虚拟 CAN 总线

```bash
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### 第二步：发送测试 CAN 报文（终端 1）

```bash
# 每 1 秒发送一条测试报文（本仓库预设的dbc文件中，发动机转速=100rpm，车速=50km/h）
while true; do cansend vcan0 100#006401F400000000; sleep 1; done
```

### 第三步：运行 ROS 2 节点（终端 2）

```bash
source ~/can_ros_env/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/can_ros_ws/install/setup.bash
python3 ~/can_ros_ws/src/can_to_ros/can_to_ros/can_to_ros_node.py --ros-args -p dbc_file:=/home/mrkedow/can_ros_ws/src/can_to_ros/example.dbc -p can_interface:=vcan0
```

### 第四步：查看发布的话题（终端 3）

```bash
source /opt/ros/jazzy/setup.bash
source ~/can_ros_ws/install/setup.bash

# 查看所有话题
ros2 topic list

# 查看发动机转速
ros2 topic echo /can_signals/enginespeed

# 查看车速
ros2 topic echo /can_signals/vehiclespeed
```

预期输出：

```
data: 100.0
---
data: 100.0
---
```

## DBC 文件说明

本仓库中的 example.dbc 文件定义了一条 CAN 报文（ID=256，即 0x100），包含两个信号：

| 信号名 | 起始位 | 长度 | 缩放因子 | 偏移量 | 单位 | 含义 |
|--------|--------|------|----------|--------|------|------|
| EngineSpeed | 0 | 16 | 1 | 0 | rpm | 发动机转速 |
| VehicleSpeed | 16 | 16 | 0.1 | 0 | km/h | 车速 |

报文数据 `00 64 01 F4 00 00 00 00` 的含义：
- 前两个字节 `00 64` = 十进制 100 → 发动机转速 = 100 × 1 + 0 = 100 rpm
- 第 3-4 字节 `01 F4` = 十进制 500 → 车速 = 500 × 0.1 + 0 = 50 km/h

## 节点工作原理

```
CAN 总线 (vcan0)
    │
    ▼
python-can (SocketCAN 驱动，读取原始报文)
    │
    ▼
cantools + example.dbc (解码为物理信号)
    │
    ▼
ROS 2 节点 (发布 Float32 话题)
    │
    ▼
ros2 topic echo (验证输出)
```

## 在实体 CAN 硬件上应用

将节点的 `can_interface` 参数从 `vcan0` 改为实际的 CAN 接口名（如 `can0`），并替换 `bustype` 为对应驱动（如 `socketcan`、`kvaser`、`vector` 等），代码无需其他修改。

## 常见错误排查

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `ModuleNotFoundError: No module named 'cantools'` | 虚拟环境未激活 | 执行 `source ~/can_ros_env/bin/activate` |
| `FileNotFoundError: example.dbc` | DBC 路径错误 | 使用绝对路径：`/home/用户名/can_ros_ws/src/can_to_ros/example.dbc` |
| `Cannot open can interface` | vcan0 未创建 | 执行 `sudo ip link add dev vcan0 type vcan` |
| `Protocol not supported` | can_raw 模块未加载 | 执行 `sudo modprobe can_raw` |
