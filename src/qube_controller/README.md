# qube_controller

A ROS2 package implementing a PID controller for the Qube rotary servo system. It subscribes to joint states, computes a velocity command using a PID loop, and publishes it to the velocity controller.

---

## Package Structure

```
qube_controller/
├── qube_controller/
│   ├── __init__.py
│   └── qube_controller_node.py   # PID controller node
├── package.xml
├── setup.py
└── setup.cfg
```

---

## Dependencies

- `rclpy`
- `sensor_msgs` - for `JointState` subscription
- `std_msgs` - for `Float64MultiArray` velocity commands
- `rcl_interfaces` - for runtime parameter callbacks

---

## Parameters

All parameters can be set at launch or changed at runtime using `ros2 param set`.

| Parameter | Default | Description |
|---|---|---|
| `kp` | `5.0` | Proportional gain |
| `ki` | `0.1` | Integral gain |
| `kd` | `0.05` | Derivative gain |
| `setpoint` | `0.0` | Target angle in radians |
| `max_output` | `10.0` | Maximum velocity command (rad/s) |

When `setpoint` is changed at runtime, the integral and derivative terms are automatically reset to avoid windup and transients.

---

## Topics

| Topic | Type | Direction | Description |
|---|---|---|---|
| `/joint_states` | `sensor_msgs/JointState` | Subscribed | Current joint position and velocity |
| `/velocity_controller/commands` | `std_msgs/Float64MultiArray` | Published | Velocity command for `motor_joint` |

---

## Usage

### Build the package

```bash
cd ~/ros2_ws
colcon build --packages-select qube_controller
source install/setup.bash
```

### Run the controller node

```bash
ros2 run qube_controller pid_node
```

### Run with custom PID gains

```bash
ros2 run qube_controller pid_node --ros-args -p kp:=8.0 -p ki:=0.2 -p kd:=0.1
```

### Change the setpoint at runtime

```bash
ros2 param set /qube_controller setpoint 1.5708   # 90 degrees
```

### Tune PID gains at runtime

```bash
ros2 param set /qube_controller kp 8.0
ros2 param set /qube_controller ki 0.2
ros2 param set /qube_controller kd 0.1
```

---

## How It Works

The `QubeControllerNode` subscribes to `/joint_states` and extracts the position of `motor_joint` on each message. It computes the time delta `dt` between callbacks and feeds the position error into the `PIDController` class, which returns a clamped velocity command. The command is then published to `/velocity_controller/commands` as a `Float64MultiArray`.

The PID output is clamped to `[-max_output, max_output]` to protect the hardware from excessive velocity commands.
