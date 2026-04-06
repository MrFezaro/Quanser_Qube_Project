import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CannyEdgeNode(Node):
    """
    A node for applying the canny edge method on an image
    """
    def __init__(self):
        super().__init__('canny_edge')

        self.subscription = self.create_subscription(
            Image,
            "image_raw",
            self.image_callback,
            1)
        self.subscription

        self.publisher = self.create_publisher(
            Image,
            'output_image',
            1)

        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error('Failed to convert image: %s' % str(e))
            return

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        median = int(cv2.mean(gray)[0])
        lower = int(max(0, 0.5 * median))
        upper = int(min(255, 1.5 * median))

        cv_edge = cv2.Canny(gray, lower, upper)
        cv_edge = cv2.cvtColor(cv_edge, cv2.COLOR_GRAY2BGR)  # ← only once

        try:
            edge_msg = self.bridge.cv2_to_imgmsg(cv_edge, "bgr8")
        except Exception as e:
            self.get_logger().error('Failed to convert image: %s' % str(e))
            return

        self.publisher.publish(edge_msg)


def main(args=None):
    rclpy.init(args=args)
    canny_edge_node = CannyEdgeNode()
    rclpy.spin(canny_edge_node)
    canny_edge_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()