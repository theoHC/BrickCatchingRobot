import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker, MarkerArray
import colorsys

def main(args=None):
    rclpy.init(args=args)
    
    arena = Arena()
    
    arena.get_logger().info('arena node initializing')

    rclpy.spin(arena)
    
    arena.destroy_node()

    rclpy.shutdown()

class Arena(Node):
    def __init__(self):
        super().__init__('arena')

        self.declare_parameter('frequency', 20)

        self.broadcaster = TransformBroadcaster(self)

        self.marktimer = self.create_timer(.05, self.marker_timer_callback)

        self.marker_publisher = self.create_publisher(MarkerArray, 'visualization_marker_array', 10)

        self.h = 1.0
        self.dh = .01


    def marker_timer_callback(self):
        # self.get_logger().info('arena node callback')

        r, g, b = colorsys.hsv_to_rgb(self.h, 1.0, 1.0)
        self.h = (self.h + self.dh) % 1.0

        markerarr = MarkerArray()
        markerarr.markers = [self.makewall(0, (5.75, -.5, .5), (11.5, 1.0, 1.0), r, g, b),
                             self.makewall(1, (-.5, 5.75, .5), (1.0, 13.5, 1.0), r, g, b),
                             self.makewall(2, (5.75, 12.0, .5), (11.5, 1.0, 1.0), r, g, b),
                             self.makewall(3, (12.0, 5.75, .5), (1.0, 13.5, 1.0), r, g, b)]
        self.marker_publisher.publish(markerarr)
    
    def makewall(self, id, pos, scale, r, g, b):
        marker = Marker()
        marker.header.frame_id = 'world'
        marker.ns = 'arena'
        marker.id = id
        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        marker.pose.position.x = pos[0]
        marker.pose.position.y = pos[1]
        marker.pose.position.z = pos[2]
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0

        marker.scale.x = scale[0]
        marker.scale.y = scale[1]
        marker.scale.z = scale[2]

        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = 1.0

        return marker
