import rclpy
from rclpy.node import Node
from pid_controller_msgs.srv import SetReference


class ReferenceInputNode(Node):

    def __init__(self):
        super().__init__("reference_input_node")
        self.client = self.create_client(SetReference, "set_reference")

        self.get_logger().info(
            "Waiting for 'set_reference' service to become available..."
        )
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available yet. Retrying...")

        self.get_logger().info(
            "'set_reference' service available. Ready to send references."
        )

    def send_reference(self, value):
        request = SetReference.Request()
        request.reference = value

        self.get_logger().info(f"Sending reference value: {value}")

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()


def main():
    rclpy.init()
    node = ReferenceInputNode()

    try:
        while rclpy.ok():

            consoleUserInput = input("Enter a new reference value (float | -π to π): ")

            try:
                userinput = float(consoleUserInput)
            except ValueError:
                node.get_logger().warn(
                    f"Invalid input '{consoleUserInput}'. Please enter a numeric value between -π and π."
                )
                continue

            response = node.send_reference(userinput)

            if response.success:
                node.get_logger().info("Reference updated successfully.")
            else:
                node.get_logger().warn(
                    "Failed to update reference. Service returned failure."
                )

    except KeyboardInterrupt:
        node.get_logger().info(
            "Keyboard interrupt received. Shutting down reference input node."
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
