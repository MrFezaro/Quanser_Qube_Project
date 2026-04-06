import os
import xacro

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    package_name = "qube_description"

    # Find the xacro file
    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        "urdf",
        "joint_model.urdf.xacro"
    )
    robot_description_content = xacro.process_file(xacro_file).toxml()

    # Publishes qubes transforms
    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description_content
        }],
        output="screen"
    )

    # Launches GUI with sliders
    node_joint_state_publisher_gui = ExecuteProcess(
        cmd=['ros2', 'run', 'joint_state_publisher_gui',
             'joint_state_publisher_gui'],
        output='screen'
    )

    # Opens RViz with a pre defined config
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=[
            '-d', [os.path.join(get_package_share_directory("qube_description"), 'config', 'config.rviz')]]
    )

    # Launches all nodes together
    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        node_rviz
    ])
