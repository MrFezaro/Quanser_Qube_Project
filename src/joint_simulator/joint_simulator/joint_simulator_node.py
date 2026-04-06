import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from rcl_interfaces.msg import SetParametersResult
import random

# https://youtu.be/wfCuPQ_6VbI?si=h02B-jiZ1c8X4tZk

### Test command ###
# ros2 run joint_simulator joint_simulator_node
# ros2 topic echo /publish_angle
# ros2 topic pub -r 10 /input_voltage std_msgs/msg/Float64 "{data: 1.0}"
# ros2 topic pub /input_voltage std_msgs/msg/Float64 "{data: 0.0}"


class JointSimulator:
    def __init__(self, voltage, noise, K, T):
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.voltage = voltage
        self.noise = noise

        # Constant
        self.K = K
        self.T = T

    def update(self, dt):
        # Transfer function
        angular_acceleration = (self.K * self.voltage - self.angular_velocity) / self.T

        # Integrate
        self.angular_velocity += angular_acceleration * dt
        self.angle += self.angular_velocity * dt + self.noise * random.random()


class JointSimulatorNode(Node):
    def __init__(self):
        super().__init__("joint_simulator_node_9")

        # Initial
        self.declare_parameter("voltage", 0.0)
        self.declare_parameter("noise", 0.0)
        self.declare_parameter("K", 230.0)
        self.declare_parameter("T", 0.15)

        # Received
        received_voltage = (
            self.get_parameter("voltage").get_parameter_value().double_value
        )
        received_noise = self.get_parameter("noise").get_parameter_value().double_value
        received_K = self.get_parameter("K").get_parameter_value().double_value
        received_T = self.get_parameter("T").get_parameter_value().double_value

        self.simulator = JointSimulator(
            received_voltage, received_noise, received_K, received_T
        )

        # Publisher
        self.publisher = self.create_publisher(Float64, "publish_angle_9", 10)

        # Subscription
        self.subscription = self.create_subscription(
            Float64, "voltage_9", self.voltage_listener, 10
        )

        "voltage" == "voltage_9"

        # Timer
        self.dt = 0.1  # 100 Hz
        self.timer = self.create_timer(self.dt, self.timer_callback)

        self.add_on_set_parameters_callback(self.parameter_callback)

    def voltage_listener(self, msg):
        self.simulator.voltage = msg.data

    def parameter_callback(self, params):
        """Callback to handle parameter updates."""
        for param in params:
            if param.name == "noise":
                if param.value >= 0.0:
                    self.simulator.noise = param.value
                    self.get_logger().info(f" noise was set: {self.simulator.noise}")

            if param.name == "K":
                if param.value >= 0.0:
                    self.simulator.K = param.value
                    self.get_logger().info(f" K was set: {self.simulator.K}")

            if param.name == "T":
                if param.value >= 0.0:
                    self.simulator.T = param.value
                    self.get_logger().info(f" T was set: {self.simulator.T}")

        return SetParametersResult(successful=True)

    def timer_callback(self):
        self.simulator.update(self.dt)

        msg = Float64()
        msg.data = self.simulator.angle
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = JointSimulatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
