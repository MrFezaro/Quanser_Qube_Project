import math
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Float64
from time import time
from pid_controller_msgs.srv import SetReference


class pidController:
    def __init__(self, p, i, d, reference):
        self.p = p
        self.i = i
        self.d = d
        self.reference = reference

        self.voltage = 0.0
        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, measurement, dt):
        error = self.reference - measurement

        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0.0 else 0.0

        self.voltage = self.p * error + self.i * self.integral + self.d * derivative

        self.previous_error = error
        return self.voltage


class PIDControllerNode(Node):
    def __init__(self):
        super().__init__("pid_controller_node_9")

        # Declare parameters
        self.declare_parameter("p", 0.01)
        self.declare_parameter("i", 0.0)
        self.declare_parameter("d", 0.0)
        self.declare_parameter("reference", 1.0)

        # Get parameters
        p = self.get_parameter("p").get_parameter_value().double_value
        i = self.get_parameter("i").get_parameter_value().double_value
        d = self.get_parameter("d").get_parameter_value().double_value
        reference = self.get_parameter("reference").get_parameter_value().double_value

        # PID controller
        self.pid = pidController(p, i, d, reference)

        # Register parameter callback
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.last_time = time()
        self.latest_measurement = 0.0

        # Publisher
        self.publish_voltage = self.create_publisher(Float64, "voltage_9", 10)

        # Subscriber
        self.measured_angle = self.create_subscription(
            Float64, "publish_angle_9", self.measurement_listener, 10
        )

        # Timer
        self.timer = self.create_timer(0.1, self.timer_callback)

        # **Create the service to update reference**
        self.srv = self.create_service(
            SetReference, "set_reference", self.set_reference_callback
        )

        self.get_logger().info(
            "PID Controller Node started with service 'set_reference'"
        )

    # --- Service callback ---
    def set_reference_callback(self, request, response):
        self.get_logger().info(
            f"Incoming service request: reference={request.reference}"
        )

        if -math.pi <= request.reference <= math.pi:
            # Update PID reference
            self.pid.reference = request.reference
            # Also update the ROS 2 parameter
            self.set_parameters(
                [
                    rclpy.parameter.Parameter(
                        "reference", rclpy.Parameter.Type.DOUBLE, request.reference
                    )
                ]
            )
            response.success = True
            self.get_logger().info(f"Reference updated to {self.pid.reference}")
        else:
            response.success = False
            self.get_logger().warn(
                f"Reference {request.reference} out of range (-π to π)"
            )

        return response

    # --- Existing callbacks ---
    def parameter_callback(self, params):
        for param in params:
            if param.name == "p" and param.value >= 0.0:
                self.pid.p = param.value
                self.get_logger().info(f"P set to {self.pid.p}")
            elif param.name == "i" and param.value >= 0.0:
                self.pid.i = param.value
                self.get_logger().info(f"I set to {self.pid.i}")
            elif param.name == "d" and param.value >= 0.0:
                self.pid.d = param.value
                self.get_logger().info(f"D set to {self.pid.d}")
            elif param.name == "reference":
                self.pid.reference = param.value
                self.get_logger().info(f"Reference set to {self.pid.reference}")

        return SetParametersResult(successful=True)

    def measurement_listener(self, msg: Float64):
        self.latest_measurement = msg.data

    def timer_callback(self):
        now = time()
        dt = now - self.last_time
        self.last_time = now

        voltage = self.pid.update(self.latest_measurement, dt)

        out = Float64()
        out.data = voltage
        self.publish_voltage.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = PIDControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Keyboard interrupt, shutting down node...")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
