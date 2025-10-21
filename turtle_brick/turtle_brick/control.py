from enum import Enum

from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from turtle_brick_interfaces.msg import Tilt
from turtlesim_msgs.msg import Pose
from visualization_msgs.msg import Marker


class BotState(Enum):
    IDLE = 0
    RETRIEVING = 1
    RETURNING = 2
    TILTING = 3


def main(args=None):
    rclpy.init(args=args)

    control = Control()

    control.get_logger().info('control node initializing')

    rclpy.spin(control)

    control.destroy_node()

    rclpy.shutdown()


class Control(Node):
    """Control the turtle robot to catch falling bricks."""

    def __init__(self):
        """Initialize publishers, subscribers, services, timers, and parameters."""
        super().__init__('control_node')

        self.declare_parameter('platform_radius', 5.0)
        self.platform_radius = self.get_parameter('platform_radius').value

        self.declare_parameter('platform_height', 5.0)
        self.platform_height = self.get_parameter('platform_height').value

        self.declare_parameter('gravity_accel', 5.0)
        self.gravity_accel = self.get_parameter('gravity_accel').value

        self.declare_parameter('max_velocity', 1.0)
        self.max_velocity = self.get_parameter('max_velocity').value

        self.create_timer(1 / 60.0, self.timer_callback)

        self.create_subscription(Empty, 'brick_dropped', self.drop_callback, 10)

        self.transformbuffer = Buffer()
        self.transformlistener = TransformListener(self.transformbuffer, self)

        self.turtle_listener = self.create_subscription(
            Pose, 'pose', self.pose_callback, 10
        )

        self.goal_broadcaster = self.create_publisher(PoseStamped, 'goal_pose', 10)

        self.marker_publisher = self.create_publisher(
            Marker, 'visualization_marker', 10
        )

        self.tilt_publisher = self.create_publisher(Tilt, 'tilt', 10)

        self.pose = Pose()

        self.goal = PoseStamped()
        self.goal.header.frame_id = 'world'

        self.tilt = 0.0

        self.state = BotState.IDLE

    def timer_callback(self):
        """Update Rviz location and publish join state."""
        disttopose = (
            (self.goal.pose.position.x - self.pose.x) ** 2
            + (self.goal.pose.position.y - self.pose.y) ** 2
        ) ** 0.5

        try:
            world_to_brick = self.transformbuffer.lookup_transform(
                'world', 'brick', rclpy.time.Time()
            )
        except Exception:
            return

        if (
            self.state is BotState.RETRIEVING
            and disttopose < 0.05
            and abs(world_to_brick.transform.translation.z - self.platform_height) < 0.1
        ):

            self.goal.pose.position.x = 5.4
            self.goal.pose.position.y = 5.4

            self.goal.header.stamp = self.get_clock().now().to_msg()
            self.goal_broadcaster.publish(self.goal)
            self.state = BotState.RETURNING
        elif self.state is BotState.RETURNING and disttopose < 0.05:
            self.state = BotState.TILTING
        elif self.state is BotState.TILTING:
            if abs(self.tilt) < 0.4:
                self.tilt += 0.01
                tiltmsg = Tilt()
                tiltmsg.angle = self.tilt
                self.tilt_publisher.publish(tiltmsg)
            else:
                self.state = BotState.IDLE

    def drop_callback(self, msg):
        """Command the turtle in response to the brick being dropped."""
        tiltmsg = Tilt()
        tiltmsg.angle = 0.0
        self.tilt_publisher.publish(tiltmsg)
        self.tilt = 0.0

        try:
            world_to_brick = self.transformbuffer.lookup_transform(
                'world', 'brick', rclpy.time.Time()
            )
        except Exception:
            return
        brick_location = (
            world_to_brick.transform.translation.x,
            world_to_brick.transform.translation.y,
            world_to_brick.transform.translation.z,
        )
        try:
            world_to_base_link = self.transformbuffer.lookup_transform(
                'world', 'base_link', rclpy.time.Time()
            )
        except Exception:
            return
        base_link_location = (
            world_to_base_link.transform.translation.x,
            world_to_base_link.transform.translation.y,
            world_to_base_link.transform.translation.z,
        )

        distance_xy = (
            (brick_location[0] - base_link_location[0]) ** 2
            + (brick_location[1] - base_link_location[1]) ** 2
        ) ** 0.5

        robot_travel_time = (distance_xy - self.platform_radius) / self.max_velocity

        height_diff = brick_location[2] - self.platform_height

        fall_time = (2 * height_diff / self.gravity_accel) ** 0.5

        if (
            robot_travel_time < fall_time
            and brick_location[2] > self.platform_height
            and 0.0 <= brick_location[0] <= 11.4
            and 0.0 <= brick_location[1] <= 11.4
        ):
            self.goal.pose.position.x = brick_location[0]
            self.goal.pose.position.y = brick_location[1]

            self.goal.header.stamp = self.get_clock().now().to_msg()

            self.goal_broadcaster.publish(self.goal)
            self.state = BotState.RETRIEVING
        else:
            text = Marker()
            text.header.frame_id = 'odom'
            text.ns = 'control'
            text.id = 0
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.text = 'Unreachable'
            text.pose.position.z = 2.0
            text.lifetime.sec = 3
            text.scale.z = 2.0
            text.color.a = 1.0
            text.color.r = 1.0
            text.color.g = 0.0
            text.color.b = 0.0

            text.header.stamp = self.get_clock().now().to_msg()
            self.marker_publisher.publish(text)

    def pose_callback(self, pose):
        """Update turtle pose."""
        self.pose = pose
