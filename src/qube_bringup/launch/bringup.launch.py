import os
import xacro
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def launch_setup(context, *args, **kwargs):
    bringup_pkg     = get_package_share_directory("qube_bringup")
    driver_pkg      = get_package_share_directory("qube_driver")
    description_pkg = get_package_share_directory("qube_description")

    # Resolve launch arguments at runtime
    simulation = LaunchConfiguration("simulation").perform(context)
    device     = LaunchConfiguration("device").perform(context)
    baud_rate  = LaunchConfiguration("baud_rate").perform(context)

    # Process xacro with resolved values
    xacro_file = os.path.join(bringup_pkg, "urdf", "controlled_qube.urdf.xacro")
    robot_description_content = xacro.process_file(
        xacro_file,
        mappings={
            "baud_rate":  baud_rate,
            "device":     device,
            "simulation": simulation,
        }
    ).toxml()
    robot_description = {"robot_description": robot_description_content}

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="screen",
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            os.path.join(bringup_pkg, "config", "qube_controllers.yaml"),  # ← qube_bringup, not qube_driver
        ],
        output="screen",
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster",
                   "--controller-manager", "/controller_manager"],
        output="screen",
    )

    velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["velocity_controller",
                   "--controller-manager", "/controller_manager"],
        output="screen",
    )

    rviz_config = os.path.join(description_pkg, "config", "config.rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        output="screen",
    )

    return [
        robot_state_publisher,
        ros2_control_node,
        TimerAction(period=3.0, actions=[joint_state_broadcaster]),
        TimerAction(period=5.0, actions=[velocity_controller]),
        rviz,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("simulation", default_value="false",
                              description="Use simulated hardware"),
        DeclareLaunchArgument("device",     default_value="/dev/ttyACM0",
                              description="Serial port device"),
        DeclareLaunchArgument("baud_rate",  default_value="115200",
                              description="Serial baud rate"),
        OpaqueFunction(function=launch_setup),
    ])