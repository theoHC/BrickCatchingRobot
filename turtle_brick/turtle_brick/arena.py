import colorsys
from enum import Enum

from geometry_msgs.msg import TransformStamped
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty as EmptyMsg
from std_srvs.srv import Empty
from tf2_ros import TransformBroadcaster
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import transforms3d
##################### Begin_Citation [3] #####################
from turtle_brick import physics
##################### End_Citation [3] #####################
from turtle_brick_interfaces.msg import Tilt
from turtle_brick_interfaces.srv import Place
from visualization_msgs.msg import Marker, MarkerArray


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
    """Simulate the arena with walls and a falling brick."""

    def __init__(self):
        """Set up params, timers, publishers, services, and the physics world."""
        super().__init__('arena')

        self.declare_parameter('wall frequency', 60)
        self.wall_frequency = self.get_parameter('wall frequency').value

        self.declare_parameter('physics frequency', 250)
        self.physics_frequency = self.get_parameter('physics frequency').value

        self.declare_parameter('gravity_accel', 5.0)
        self.gravity_accel = self.get_parameter('gravity_accel').value

        self.declare_parameter('platform_radius', 5.0)
        self.platform_radius = self.get_parameter('platform_radius').value

        self.declare_parameter('platform_height', 5.0)
        self.platform_height = self.get_parameter('platform_height').value

        self.broadcaster = TransformBroadcaster(self)
        self.transformbuffer = Buffer()
        self.transformlistener = TransformListener(self.transformbuffer, self)

        self.marktimer = self.create_timer(
            1 / self.wall_frequency, self.wall_timer_callback
        )
        self.phystimer = self.create_timer(
            1 / self.physics_frequency, self.physics_timer_callback
        )

        self.marker_publisher = self.create_publisher(
            MarkerArray, 'visualization_marker_array', 10
        )

        self.droppub = self.create_publisher(EmptyMsg, 'brick_dropped', 10)

        self.h = 1.0
        self.dh = 0.01

        self.BrickState = BrickState.PLACED
        self.bricktrans = TransformStamped()
        self.bricktrans.header.frame_id = 'world'
        self.bricktrans.child_frame_id = 'brick'

        self.physics = physics.World(
            (0.0, 0.0, 5.0), self.gravity_accel, 5.0, 1 / self.physics_frequency
        )

        self.place = self.create_service(Place, 'place', self.place_callback)

        self.drop = self.create_service(Empty, 'drop', self.drop_callback)

        self.tilt_listener = self.create_subscription(
            Tilt, 'tilt', self.tilt_callback, 10
        )

        self.tilt = 0.0

    def wall_timer_callback(self):
        """Timer to place the walls and the brick markers. Makes them rainbow too."""
        # self.get_logger().info('arena node callback')

        r, g, b = colorsys.hsv_to_rgb(self.h, 0.75, 1.0)
        br, bg, bb = colorsys.hsv_to_rgb((self.h + 0.5) % 1.0, 0.75, 1.0)
        self.h = (self.h + self.dh) % 1.0

        markerarr = MarkerArray()
        markerarr.markers = [
            self.makecube(0, (5.75, -0.5, 0.5), (11.5, 1.0, 1.0), r, g, b),
            self.makecube(1, (-0.5, 5.75, 0.5), (1.0, 13.5, 1.0), r, g, b),
            self.makecube(2, (5.75, 12.0, 0.5), (11.5, 1.0, 1.0), r, g, b),
            self.makecube(3, (12.0, 5.75, 0.5), (1.0, 13.5, 1.0), r, g, b),
            self.makecube(
                4, (0.0, 0.0, 0.25), (0.5, 0.5, 0.5), br, bg, bb, frame='brick'
            ),
        ]
        self.marker_publisher.publish(markerarr)

    def makecube(self, markerid, pos, scale, r, g, b, frame='world'):
        """
        Create a cube marker.

        Args:
        ----
            id - the marker id
            pos - (x,y,z) position of the cube center
            scale - (x,y,z) scale of the cube
            r - red color component (0 to 1)
            g - green color component (0 to 1)
            b - blue color component (0 to 1)
            frame - the reference frame of the cube

        Returns
        -------
            marker - the cube marker

        """
        marker = Marker()
        marker.header.frame_id = frame
        marker.ns = 'arena'
        marker.id = markerid
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
        """Timer to update the physics simulation of the brick based on its current state."""
        if self.BrickState == BrickState.PLACED:
            pass
        elif self.BrickState == BrickState.SIM:
            self.physics.drop()
            self.bricktrans.transform.translation.x = self.physics.brick[0]
            self.bricktrans.transform.translation.y = self.physics.brick[1]
            self.bricktrans.transform.translation.z = self.physics.brick[2]

            try:
                self.platform_to_brick = self.transformbuffer.lookup_transform(
                    'platform_link', 'brick', rclpy.time.Time()
                )
                # self.get_logger().info(f'Transform is: {self.platform_to_brick}')

            finally:
                pass

            if (
                abs(self.bricktrans.transform.translation.z - self.platform_height)
                < 0.05
                and self.platform_to_brick.transform.translation.x**2
                + self.platform_to_brick.transform.translation.y**2
                < self.platform_radius**2
            ):
                self.get_logger().info(
                    repr(transformstamped_to_matrix(self.platform_to_brick))
                )
                self.BrickState = BrickState.CAUGHT
                self.platform_to_brick.transform.translation.z = 0.05

                self.physics.brick = (
                    0.0,
                    0.0,
                    self.platform_to_brick.transform.translation.x,
                )

                self.physics.falling = False

        elif self.BrickState == BrickState.CAUGHT:

            try:
                self.world_to_platform = self.transformbuffer.lookup_transform(
                    'world', 'platform_link', rclpy.time.Time()
                )
            except Exception:
                return

            self.physics.theta = -1 * self.tilt

            self.physics.drop()

            self.platform_to_brick.transform.translation.x = self.physics.brick[2]

            self.bricktrans = matrix_to_transformstamped(
                transformstamped_to_matrix(self.world_to_platform)
                @ transformstamped_to_matrix(self.platform_to_brick)
            )

            brickfromplatformdist = np.sqrt(
                (self.platform_to_brick.transform.translation.x) ** 2
                + self.platform_to_brick.transform.translation.y**2
            )

            if brickfromplatformdist > self.platform_radius + 0.25:
                self.get_logger().info('Brick has slid off the platform!')
                self.BrickState = BrickState.PLACED

        self.bricktrans.header.stamp = self.get_clock().now().to_msg()
        self.broadcaster.sendTransform(self.bricktrans)

    def drop_callback(self, request, response):
        """
        Initiate the dropping of the brick if the brick is in the placed state.

        Args:
        ----
        request :
            Empty request
        response :
            Empty response
        Returns
        -------
        response :
            Empty response

        """
        if self.BrickState == BrickState.PLACED:
            self.get_logger().info('Dropping the brick!')
            self.BrickState = BrickState.SIM
            self.physics.falling = True

        self.droppub.publish(EmptyMsg())

        return response

    def place_callback(self, request, response):
        """
        Place the brick at a specified location and reset its state to PLACED.

        Args:
        ----
        request :
            Place request containing the point to place the brick
        response :
            Empty response
        Returns
        -------
        response :
            Empty response

        """
        self.BrickState = BrickState.PLACED
        self.get_logger().info(
            f'Placing the brick at ({request.point.x}, {request.point.y}, {request.point.z})'
        )
        self.bricktrans.transform.translation.x = request.point.x
        self.bricktrans.transform.translation.y = request.point.y
        self.bricktrans.transform.translation.z = request.point.z
        self.bricktrans.transform.rotation.x = 0.0
        self.bricktrans.transform.rotation.y = 0.0
        self.bricktrans.transform.rotation.z = 0.0
        self.bricktrans.transform.rotation.w = 1.0

        self.physics.brick = (request.point.x, request.point.y, request.point.z)
        self.physics.theta = np.pi / 2

        return response

    def tilt_callback(self, tilt):
        """Set tilt angle from message."""
        self.tilt = tilt.angle


############ Begin_Citation [4] #############


def transformstamped_to_matrix(t: TransformStamped) -> np.ndarray:
    """
    Convert a TransformStamped message to a 4×4 transformation matrix.

    Args:
    ----
    t :
        the TransformStamped message
    Returns:
    -------
    T :
        the 4×4 transformation matrix

    """
    # Extract translation
    trans = np.array(
        [
            t.transform.translation.x,
            t.transform.translation.y,
            t.transform.translation.z,
        ]
    )

    # Extract quaternion (w, x, y, z)
    q = np.array(
        [
            t.transform.rotation.w,
            t.transform.rotation.x,
            t.transform.rotation.y,
            t.transform.rotation.z,
        ]
    )

    # Convert quaternion to rotation matrix
    R = transforms3d.quaternions.quat2mat(q)  # 3×3

    # Build full 4×4 transformation matrix
    T = transforms3d.affines.compose(trans, R, np.ones(3))  # no scaling
    return T


def matrix_to_transformstamped(
    T: np.ndarray, parent_frame: str = 'world', child_frame: str = 'brick'
) -> TransformStamped:
    """
    Convert a 4×4 transformation matrix to a TransformStamped message.

    Args:
    ---
    T :
        the 4×4 transformation matrix
    parent_frame :
        the parent frame id
    child_frame :
        the child frame id

    Returns
    -------
    msg:
        the TransformStamped message

    """
    # Extract translation, rotation, and scale
    trans, rot, zoom, shear = transforms3d.affines.decompose(T)

    # Convert rotation matrix to quaternion (returns w, x, y, z)
    q = transforms3d.quaternions.mat2quat(rot)

    # Build the TransformStamped message
    msg = TransformStamped()
    msg.header.frame_id = parent_frame
    msg.child_frame_id = child_frame

    msg.transform.translation.x = trans[0]
    msg.transform.translation.y = trans[1]
    msg.transform.translation.z = trans[2]

    msg.transform.rotation.w = q[0]
    msg.transform.rotation.x = q[1]
    msg.transform.rotation.y = q[2]
    msg.transform.rotation.z = q[3]

    return msg


############ End_Citation [4] #############
