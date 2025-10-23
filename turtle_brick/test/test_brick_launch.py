import unittest

from geometry_msgs.msg import Twist
from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import launch_testing
import pytest
import rclpy


# Mark the launch description generation as a rostest
# Also, it's called generate_test_description() for a test
# But it still returns a LaunchDescription
@pytest.mark.rostest
def generate_test_description():
    turtle_brick_share = FindPackageShare('turtle_brick')
    turtle_yaml = PathJoinSubstitution([turtle_brick_share, 'turtle.yaml'])

    return (
        LaunchDescription([
            Node(package='turtle_brick',
                 executable='turtlebot',
                 parameters=[turtle_yaml]),
            launch_testing.actions.ReadyToTest()
            ]))


class TestCMDVelFrequency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run one time, when the testcase is loaded."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Run one time, when testcase is unloaded."""
        rclpy.shutdown()

    def setUp(self):
        """Run before every test."""
        self.node = rclpy.create_node('test_node')

        self.node.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        self.received_msgs = 0

    def tearDown(self):
        """Run after every test."""
        self.node.destroy_node()

    def test_cmd_vel_freq(self, launch_service, proc_output):
        """Test the frequency at which cmd_vel messages are published."""
        start_time = self.node.get_clock().now()

        while self.node.get_clock().now() - start_time < rclpy.duration.Duration(seconds=10.0):
            rclpy.spin_once(self.node)

        self.node.get_logger().info(f'received messages: {self.received_msgs}')

        assert abs(self.received_msgs - 1000) < 100

    def cmd_vel_callback(self, msg):
        self.received_msgs += 1
