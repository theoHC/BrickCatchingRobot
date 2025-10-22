from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Shared package path
    turtle_brick_share = FindPackageShare('turtle_brick')

    # File paths
    show_turtle_launch = PathJoinSubstitution([turtle_brick_share, 'show_turtle.launch.xml'])
    turtle_yaml = PathJoinSubstitution([turtle_brick_share, 'turtle.yaml'])
    rviz_file = PathJoinSubstitution([turtle_brick_share, 'run_turtle.rviz'])

    # Include the XML launch file (works with any frontend)
    show_turtle = IncludeLaunchDescription(
        FrontendLaunchDescriptionSource(show_turtle_launch),
        launch_arguments={'use_jsp': 'none'}.items()
    )

    # Turtlesim node
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        parameters=[{'holonomic': True}]
    )

    # Turtlebot node
    turtlebot_node = Node(
        package='turtle_brick',
        executable='turtlebot',
        parameters=[turtle_yaml],
        remappings=[
            ('pose', '/turtle1/pose'),
            ('cmd_vel', '/turtle1/cmd_vel'),
        ]
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file]
    )

    return LaunchDescription([
        show_turtle,
        turtlesim_node,
        turtlebot_node,
        rviz_node,
    ])
