#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import cantools
import can

class CanToRosNode(Node):
    def __init__(self):
        super().__init__('can_to_ros_node')
        self.declare_parameter('dbc_file', 'example.dbc')
        self.declare_parameter('can_interface', 'vcan0')
        dbc_file = self.get_parameter('dbc_file').get_parameter_value().string_value
        can_interface = self.get_parameter('can_interface').get_parameter_value().string_value

        self.db = cantools.database.load_file(dbc_file)
        # 为每个信号创建 publisher
        self.pubs = {}
        for msg in self.db.messages:
            for sig in msg.signals:
                topic = '/can_signals/' + sig.name.lower()
                self.pubs[sig.name] = self.create_publisher(Float32, topic, 10)

        self.bus = can.interface.Bus(channel=can_interface, bustype='socketcan')
        self.timer = self.create_timer(0.01, self.timer_callback)  # 100Hz

    def timer_callback(self):
        msg = self.bus.recv(timeout=0.0)
        if msg is not None:
            try:
                signals = self.db.decode_message(msg.arbitration_id, msg.data)
                for sig_name, sig_value in signals.items():
                    ros_msg = Float32()
                    ros_msg.data = float(sig_value)
                    self.pubs[sig_name].publish(ros_msg)
                    self.get_logger().info(f"Published {sig_name} = {sig_value}")
            except Exception as e:
                self.get_logger().warn(f"Decode error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = CanToRosNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()