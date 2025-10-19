from std_srvs.srv import Empty
from turtle_brick_interfaces.msg import Tilt
import rclpy
from rclpy.node import Node
from tf2_ros.transform_listener import TransformListener
from tf2_ros.buffer import Buffer
from turtlesim_msgs.msg import Pose
from visualization_msgs.msg import Marker
from geometry_msgs.msg import PoseStamped

def main(args=None):
    rclpy.init(args=args)
    
    arena = Arena()
    
    arena.get_logger().info('arena node initializing')

    rclpy.spin(arena)
    
    arena.destroy_node()

    rclpy.shutdown()

class Control(Node):
    def __init__(self):
        super().__init__('control_node')

        self.declare_parameter('platform_radius', 5.0)
        self.platform_radius = self.get_parameter('platform_radius').value

        self.declare_parameter('platform_height', 5.0)
        self.platform_height = self.get_parameter('platform_height').value

        self.declare_parameter('gravity_accel', 5.0)
        self.gravity_accel = self.get_parameter('gravity_accel').value

        self.declare_parameter('max_velocity', 1.0)
        self.max_velocity = self.get_parameter('max_velocity').value

        self.create_timer(1/60.0, self.timer_callback)

        self.create_subscription(Empty, 'brick_dropped', self.drop_callback, 10)

        self.transformbuffer = Buffer()
        self.transformlistener = TransformListener(self.transformbuffer, self)

        self.turtle_listener = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
    
    def timer_callback(self):
        pass

    def drop_callback(self, msg):
        world_to_brick = self.transformbuffer.lookup_transform('world', 'brick', rclpy.time.Time())
        brick_location = (world_to_brick.transform.translation.x,world_to_brick.transform.translation.y,world_to_brick.transform.translation.z)
        world_to_base_link = self.transformbuffer.lookup_transform('world', 'base_link', rclpy.time.Time())
        base_link_location = (world_to_base_link.transform.translation.x,world_to_base_link.transform.translation.y,world_to_base_link.transform.translation.z)
        
        distance_xy = ((brick_location[0]-base_link_location[0])**2 + (brick_location[1]-base_link_location[1])**2)**0.5
