from math import pi

from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import Vector3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from turtlesim_msgs.msg import Pose
from sensor_msgs.msg import JointState
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup

def main(args=None):
    rclpy.init(args=args)
    
    turtle_robot = TurtleRobot()
    
    turtle_robot.get_logger().info('turtle_robot node initializing')

    rclpy.spin(turtle_robot)
    
    turtle_robot.destroy_node()

    rclpy.shutdown()

class TurtleRobot(Node):
    """Uses the turtlesim node to control the location of a robot
    """

    def __init__(self):
        super().__init__('turtle_robot')

        self.special_callback = MutuallyExclusiveCallbackGroup()

        self.static_broadcaster = StaticTransformBroadcaster(self)

        self.broadcaster = TransformBroadcaster(self)

        self.turtle_listener = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        self.timer = self.create_timer(1/100, self.timer_callback)

        self.bot_joints = self.create_publisher(JointState, '/joint_states', 10)

        self.setup_odom = False

    def pose_callback(self, pose):
        if not self.setup_odom:
            self.setup_odom = True
            world_odom_tf = TransformStamped()
            world_odom_tf.header.frame_id = 'world'
            world_odom_tf.child_frame_id = 'odom'
            world_odom_tf.header.stamp = self.get_clock().now().to_msg()
            world_odom_tf.transform.translation = Vector3(x=pose.x, y=pose.y, z=0.0)
            self.static_broadcaster.sendTransform(world_odom_tf)

            self.startloc = (pose.x, pose.y)
        self.pose = pose
        

    def timer_callback(self):
        self.get_logger().info('Tick callback')
        if self.setup_odom:
            odom_bot_tf = TransformStamped()
            odom_bot_tf.header.frame_id = 'odom'
            odom_bot_tf.child_frame_id = 'base_link'
            odom_bot_tf.transform.translation=Vector3(x=self.pose.x - self.startloc[0], y=self.pose.y - self.startloc[1], z=0.0)

            odom_bot_tf.header.stamp = self.get_clock().now().to_msg()
            self.broadcaster.sendTransform(odom_bot_tf)
        
