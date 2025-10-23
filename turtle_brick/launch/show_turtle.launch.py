# &&&&&&&&&&&&&& Begin_Citation [7] &&&&&&&&&&&&&&
from launch import LaunchDescription  # noqa: I001
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch argument
    use_jsp = LaunchConfiguration('use_jsp')

    # Paths
    turtle_brick_share = FindPackageShare('turtle_brick')
    urdf_file = PathJoinSubstitution([turtle_brick_share, 'turtle_bot.urdf.xacro'])
    rviz_file = PathJoinSubstitution([turtle_brick_share, 'peruse_turtle.rviz'])

    # Declare argument
    declare_use_jsp = DeclareLaunchArgument(
        'use_jsp',
        default_value='gui',
        description="The joint state publisher to use: 'gui', 'jsp', or 'none'."
    )

    # Robot State Publisher (loads xacro)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Command([
                FindExecutable(name='xacro'), ' ',
                urdf_file
            ])
        }]
    )

    # Joint State Publisher (GUI)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition=IfCondition(PythonExpression(["'", use_jsp, "' == 'gui'"]))
    )

    # Joint State Publisher (no GUI)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=IfCondition(PythonExpression(["'", use_jsp, "' == 'jsp'"]))
    )

    # RViz (disabled when use_jsp == 'none')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file],
        condition=UnlessCondition(PythonExpression(["'", use_jsp, "' == 'none'"]))
    )

    # Return all actions as part of LaunchDescription
    return LaunchDescription([
        declare_use_jsp,
        robot_state_publisher,
        joint_state_publisher_gui,
        joint_state_publisher,
        rviz
    ])
# &&&&&&&&&&&&&& End_Citation [7] &&&&&&&&&&&&&& #
