from launch import LaunchDescription

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources.xml_launch_description_source import (
    XMLLaunchDescriptionSource,
)
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Common package share directory
    turtle_brick_share = FindPackageShare('turtle_brick')

    # Paths
    show_turtle_launch = PathJoinSubstitution([turtle_brick_share, 'show_turtle.launch.xml'])
    turtle_yaml = PathJoinSubstitution([turtle_brick_share, 'turtle.yaml'])
    rviz_file = PathJoinSubstitution([turtle_brick_share, 'run_turtle.rviz'])

    # Include show_turtle.launch.xml with argument override
    show_turtle = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(show_turtle_launch),
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
            ('cmd_vel', '/turtle1/cmd_vel')
        ]
    )

    # RViz node
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file]
    )

    return LaunchDescription([
        show_turtle,
        turtlesim_node,
        turtlebot_node,
        rviz
    ])
