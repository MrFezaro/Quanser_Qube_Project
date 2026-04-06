# qube_bringup

A ROS2 bringup package for the Qube rotary servo system. It brings up the full control stack including the hardware interface, controller manager, joint state broadcaster, velocity controller, and RViz2 visualization.

---

## Package Structure

```
qube_bringup/
├── config/
│   ├── qube_controllers.yaml     # Controller manager and controller configuration
│   └── config.rviz               # RViz2 configuration (from qube_description)
├── launch/
│   └── bringup.launch.py         # Main launch file
├── urdf/
│   └── controlled_qube.urdf.xacro  # URDF with ros2_control hardware interface
├── package.xml
├── setup.py
└── setup.cfg
```

---

## Dependencies

- `qube_description` - provides the robot URDF macro and RViz config
- `qube_driver` - provides the ros2_control hardware interface
- `robot_state_publisher`
- `controller_manager`
- `joint_state_broadcaster`
- `velocity_controllers`
- `rviz2`
- `xacro`

---

## Launch Arguments

The launch file exposes the following arguments that can be passed directly on the command line:

| Argument | Default | Description |
|---|---|---|
| `simulation` | `false` | Use simulated hardware instead of real hardware |
| `device` | `/dev/ttyACM0` | Serial port device for the Qube |
| `baud_rate` | `115200` | Serial baud rate |

---

## Usage

### Build the package

```bash
cd ~/ros2_ws
colcon build --packages-select qube_bringup
source install/setup.bash
```

### Launch with default parameters (real hardware)

```bash
ros2 launch qube_bringup bringup.launch.py
```

### Launch in simulation mode

```bash
ros2 launch qube_bringup bringup.launch.py simulation:=true
```

### Launch with a custom serial port or baud rate

```bash
ros2 launch qube_bringup bringup.launch.py device:=/dev/ttyUSB0 baud_rate:=9600
```

---

## What Gets Started

The launch file starts the following nodes in order:

1. `robot_state_publisher` - publishes the robot description and TF transforms
2. `ros2_control_node` - starts the controller manager with the hardware interface
3. `joint_state_broadcaster` - spawned after 3 seconds, broadcasts joint states
4. `velocity_controller` - spawned after 5 seconds, enables velocity commands on `motor_joint`
5. `rviz2` - opens RViz2 with the pre-configured view from `qube_description`

The delays on the controller spawners ensure the controller manager is fully up before spawning.

---

## Controller Configuration

Controllers are configured in `config/qube_controllers.yaml`:

- Controller manager update rate: **100 Hz**
- `joint_state_broadcaster` - broadcasts joint states to `/joint_states`
- `velocity_controller` - `JointGroupVelocityController` on `motor_joint` via the velocity interface
