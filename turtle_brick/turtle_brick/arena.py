import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker, MarkerArray
import colorsys
from enum import Enum
from tf2_ros.transform_listener import TransformListener
from tf2_ros.buffer import Buffer
import tf2_ros
from geometry_msgs.msg import Transform, TransformStamped
from turtle_brick_interfaces.srv import Place
from std_srvs.srv import Empty
##################### Begin_Citation [3] #####################
from turtle_brick import physics
##################### End_Citation [3] #####################

class BrickState(Enum):
    PLACED = 1
    SIM = 2
    CAUGHT = 3

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

        self.declare_parameter('wall frequency', 60)
        self.wall_frequency = self.get_parameter('wall frequency').value

        self.declare_parameter('physics frequency', 250)
        self.physics_frequency = self.get_parameter('physics frequency').value

        self.declare_parameter('gravity_accel', 5.0)
        self.gravity_accel = self.get_parameter('gravity_accel').value

        self.broadcaster = TransformBroadcaster(self)
        self.transformbuffer= Buffer()
        self.transformlistener = TransformListener(self.transformbuffer, self)

        self.marktimer = self.create_timer(1/self.wall_frequency, self.wall_timer_callback)
        self.phystimer = self.create_timer(1/self.physics_frequency, self.physics_timer_callback)

        self.marker_publisher = self.create_publisher(MarkerArray, 'visualization_marker_array', 10)

        self.h = 1.0
        self.dh = .01

        self.BrickState = BrickState.PLACED
        self.bricktrans = TransformStamped()
        self.bricktrans.header.frame_id = 'world'
        self.bricktrans.child_frame_id = 'brick'

        self.physics = physics.World((0.0, 0.0, 5.0), self.gravity_accel, 5.0, 1/self.physics_frequency)

        self.place = self.create_service(Place, 'place', self.place_callback)

        self.drop = self.create_service(Empty, 'drop', self.drop_callback)


    def wall_timer_callback(self):
        # self.get_logger().info('arena node callback')

        r, g, b = colorsys.hsv_to_rgb(self.h, .75, 1.0)
        br, bg, bb = colorsys.hsv_to_rgb((self.h + 0.5) % 1.0, .75, 1.0)
        self.h = (self.h + self.dh) % 1.0

        markerarr = MarkerArray()
        markerarr.markers = [self.makecube(0, (5.75, -.5, .5), (11.5, 1.0, 1.0), r, g, b),
                             self.makecube(1, (-.5, 5.75, .5), (1.0, 13.5, 1.0), r, g, b),
                             self.makecube(2, (5.75, 12.0, .5), (11.5, 1.0, 1.0), r, g, b),
                             self.makecube(3, (12.0, 5.75, .5), (1.0, 13.5, 1.0), r, g, b),
                             self.makecube(4, (0.0,0.0,0.25), (0.5, 0.5, .5), br, bg, bb, frame='brick')]
        self.marker_publisher.publish(markerarr)
    
    def makecube(self, id, pos, scale, r, g, b, frame='world'):
        marker = Marker()
        marker.header.frame_id = frame
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

        marker.header.stamp = self.get_clock().now().to_msg()
        return marker
    
    def physics_timer_callback(self):
        if self.BrickState == BrickState.PLACED:
            pass
        elif self.BrickState == BrickState.SIM:
            self.physics.drop()
            self.bricktrans.transform.translation.x = self.physics.brick[0]
            self.bricktrans.transform.translation.y = self.physics.brick[1]
            self.bricktrans.transform.translation.z = self.physics.brick[2]

        self.bricktrans.header.stamp = self.get_clock().now().to_msg()
        self.broadcaster.sendTransform(self.bricktrans)

    def drop_callback(self, request, response):
        if self.BrickState == BrickState.PLACED:
            self.get_logger().info('Dropping the brick!')
            self.BrickState = BrickState.SIM
        else:
            self.get_logger().info('Brick already dropped!')

        return response
    
    def place_callback(self, request, response):
        self.BrickState = BrickState.PLACED
        self.get_logger().info(f'Placing the brick at ({request.point.x}, {request.point.y}, {request.point.z})')
        self.bricktrans.transform.translation.x = request.point.x
        self.bricktrans.transform.translation.y = request.point.y
        self.bricktrans.transform.translation.z = request.point.z
        self.bricktrans.transform.rotation.x = 0.0
        self.bricktrans.transform.rotation.y = 0.0
        self.bricktrans.transform.rotation.z = 0.0
        self.bricktrans.transform.rotation.w = 1.0

        self.physics.brick = (request.point.x, request.point.y, request.point.z)

        return response