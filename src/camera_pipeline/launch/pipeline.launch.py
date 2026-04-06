from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    calibration_file = os.path.join(
        get_package_share_directory('camera_pipeline'),
        'config',
        'ost.yaml'
    )

    # Resolve symlink to get actual device path
    camera_symlink = '/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera_SN0001-video-index0'
    camera_device = os.path.realpath(camera_symlink)  # resolves to /dev/video2 or /dev/video4

    return LaunchDescription([
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='usb_cam',
            parameters=[{
                'video_device': camera_device,   # ← now uses resolved path
                'camera_info_url': 'file://' + calibration_file,
                'camera_name': 'narrow_stereo',
                'framerate': 30.0,
                'image_width': 640,
                'image_height': 480,
                'pixel_format': 'mjpeg2rgb',
            }]
        ),
        Node(
            package='image_proc',
            executable='rectify_node',
            name='rectify_node',
            parameters=[{'queue_size': 1}],
            remappings=[
                ('image', '/image_raw'),
                ('camera_info', '/camera_info'),
                ('image_rect', '/image_rect'),
            ]
        ),
        Node(
            package='camera_pipeline',
            executable='gaussian_blur',
            name='gaussian_blur',
            remappings=[
                ('image_raw', '/image_rect'),
                ('output_image', '/image_blurred'),
            ]
        ),
        Node(
            package='camera_pipeline',
            executable='canny_edge',
            name='canny_edge',
            remappings=[
                ('image_raw', '/image_blurred'),
                ('output_image', '/image_output'),
            ]
        ),
    ])