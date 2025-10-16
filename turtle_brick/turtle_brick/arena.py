import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker

def main(args=None):
    rclpy.init(args=args)
    
    arena = Arena()
    
    arena.get_logger().info('turtle_robot node initializing')

    rclpy.spin(arena)
    
    arena.destroy_node()

    rclpy.shutdown()

class Arena(Node):
    def __init__(self):
        super().__init__('arena')

        self.declare_parameter('frequency', 20)

        self.broadcaster = TransformBroadcaster(self)

        self.timer = self.create_timer(1.0, self.timer_callback)

        self.marker_publisher = self.create_publisher(Marker, 'visualization_marker', 10)

        markone = Marker()
        markone.header.frame_id = "world"
        markone.type = Marker.CUBE
        markone.action = Marker.ADD

