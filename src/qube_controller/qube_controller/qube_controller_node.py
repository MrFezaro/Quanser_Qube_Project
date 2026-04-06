import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray, MultiArrayDimension, MultiArrayLayout
import math


class PIDController:
    def __init__(self, kp, ki, kd, max_output=10.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_output = max_output

        self._integral = 0.0
        self._prev_error = 0.0

    def compute(self, setpoint, measured, dt):
        error = setpoint - measured

        self._integral += error * dt
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        output = (self.kp * error
                + self.ki * self._integral
                + self.kd * derivative)

        # Clamp output
        return max(-self.max_output, min(self.max_output, output))

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0


class QubeControllerNode(Node):
    def __init__(self):
        super().__init__("qube_controller")

        # ── Parameters ────────────────────────────────────────────────────
        self.declare_parameter("kp", 5.0)
        self.declare_parameter("ki", 0.1)
        self.declare_parameter("kd", 0.05)
        self.declare_parameter("setpoint", 0.0)       # target angle in radians
        self.declare_parameter("max_output", 10.0)

        kp         = self.get_parameter("kp").value
        ki         = self.get_parameter("ki").value
        kd         = self.get_parameter("kd").value
        max_output = self.get_parameter("max_output").value

        self._setpoint = self.get_parameter("setpoint").value
        self.add_on_set_parameters_callback(self._parameter_callback)
        self._pid = PIDController(kp, ki, kd, max_output)

        # ── State ─────────────────────────────────────────────────────────
        self._position = 0.0
        self._velocity = 0.0
        self._last_time = None

        # ── Subscriber ────────────────────────────────────────────────────
        self._sub = self.create_subscription(
            JointState,
            "/joint_states",
            self._joint_state_callback,
            10,
        )

        # ── Publisher ─────────────────────────────────────────────────────
        self._pub = self.create_publisher(
            Float64MultiArray,
            "/velocity_controller/commands",
            10,
        )

        self.get_logger().info(
            f"Qube PID controller started | "
            f"kp={kp} ki={ki} kd={kd} | "
            f"setpoint={math.degrees(self._setpoint):.1f} deg"
        )

    def _parameter_callback(self, params):
            for param in params:
                if param.name == "setpoint":
                    self._setpoint = param.value
                    self._pid.reset()  # reset integral/derivative on setpoint change
                    self.get_logger().info(
                        f"Setpoint updated to {math.degrees(self._setpoint):.1f} deg"
                    )
            return SetParametersResult(successful=True)

    def _joint_state_callback(self, msg: JointState):
        # Find motor_joint in the message
        if "motor_joint" not in msg.name:
            return

        idx = msg.name.index("motor_joint")
        self._position = msg.position[idx] if msg.position else 0.0
        self._velocity = msg.velocity[idx] if msg.velocity else 0.0

        # Compute dt
        now = self.get_clock().now()
        if self._last_time is None:
            self._last_time = now
            return
        dt = (now - self._last_time).nanoseconds * 1e-9
        self._last_time = now

        if dt <= 0.0:
            return

        # PID → velocity command
        command = self._pid.compute(self._setpoint, self._position, dt)

        # Publish as Float64MultiArray
        # MultiArrayLayout must be set correctly — data lives in a flat array,
        # with dim describing its shape.
        cmd_msg = Float64MultiArray()
        cmd_msg.layout = MultiArrayLayout()
        cmd_msg.layout.dim = [
            MultiArrayDimension(
                label="commands",
                size=1,
                stride=1,
            )
        ]
        cmd_msg.layout.data_offset = 0
        cmd_msg.data = [command]

        self._pub.publish(cmd_msg)

        self.get_logger().debug(
            f"pos={math.degrees(self._position):.2f}° "
            f"vel={self._velocity:.3f} rad/s  "
            f"cmd={command:.4f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = QubeControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()