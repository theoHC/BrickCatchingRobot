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
    run_turtle_launch = PathJoinSubstitution([turtle_brick_share, 'run_turtle.launch.xml'])
    turtle_yaml = PathJoinSubstitution([turtle_brick_share, 'turtle.yaml'])

    # Include the run_turtle launch file
    run_turtle = IncludeLaunchDescription(
        FrontendLaunchDescriptionSource(run_turtle_launch)
    )

    # Arena node
    arena_node = Node(
        package='turtle_brick',
        executable='arena',
        parameters=[turtle_yaml]
    )

    # Control node
    control_node = Node(
        package='turtle_brick',
        executable='control',
        parameters=[turtle_yaml],
        remappings=[
            ('pose', '/turtle1/pose')
        ]
    )

    # Return the composed launch description
    return LaunchDescription([
        run_turtle,
        arena_node,
        control_node
    ])
