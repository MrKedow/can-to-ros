from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    # 获取包路径
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 声明参数
    dbc_file_arg = DeclareLaunchArgument(
        'dbc_file',
        default_value=os.path.join(pkg_dir, 'example.dbc'),
        description='DBC 文件路径'
    )

    can_interface_arg = DeclareLaunchArgument(
        'can_interface',
        default_value='vcan0',
        description='CAN 接口名称'
    )

    # 节点配置
    can_to_ros_node = Node(
        package='can_to_ros',
        executable='can_to_ros_node.py',
        name='can_to_ros_node',
        output='screen',
        parameters=[{
            'dbc_file': LaunchConfiguration('dbc_file'),
            'can_interface': LaunchConfiguration('can_interface'),
        }]
    )

    return LaunchDescription([
        dbc_file_arg,
        can_interface_arg,
        can_to_ros_node,
    ])