from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # PID controller parameters
    kp_arg = DeclareLaunchArgument('p', default_value='0.05', description='Proportional gain')
    ki_arg = DeclareLaunchArgument('i', default_value='0.0', description='Integral gain')
    kd_arg = DeclareLaunchArgument('d', default_value='0.0', description='Derivative gain')


    # Joint simulator parameters
    noise_arg = DeclareLaunchArgument('noise', default_value='0.0', description='Noise level factor')
    K_arg = DeclareLaunchArgument('K', default_value='200.0', description='System gain')
    T_arg = DeclareLaunchArgument('T', default_value='0.15', description='Time constant')

    return LaunchDescription(
        [
            # PID controller parameters
            kp_arg,
            ki_arg,
            kd_arg,

            # PID controller
            Node(
                package="pid_controller",
                executable="pid_controller_node",
                name="pid_controller",
                namespace="Assignment_2",
                output="screen",
                parameters=[{
                    'p': LaunchConfiguration('p'),
                    'i': LaunchConfiguration('i'),
                    'd': LaunchConfiguration('d'),
                }]
            ),
            
            # Joint simulator parameters
            noise_arg,
            K_arg,
            T_arg,
            
            # Joint simulator
            Node(
                package="joint_simulator",
                executable="joint_simulator_node",
                name="joint_simulator",
                namespace="Assignment_2",
                output="screen",
                parameters=[{
                    'noise': LaunchConfiguration('noise'),
                    'K': LaunchConfiguration('K'),
                    'T': LaunchConfiguration('T'),
                }]
            ),
            
            # tbh no idea
            Node(
                package="pid_controller",
                executable="reference_input_node",
                name="reference_input",
                namespace="Assignment_2",
                output="screen",
                prefix="gnome-terminal --", # starts a terminal
            ),
        ]
    )
