# qube_description

A ROS2 package containing the URDF description of the Qube rotary servo system. It provides the robot model, RViz configuration, and a launch file for visualizing the model.

---

## Package Structure

```
joint_description/
├── config/
│   └── config.rviz                      # RViz2 configuration file
├── launch/
│   └── view_model.launch.py             # Launch file for visualization
├── urdf/
│   ├── joint_model.urdf.xacro           # Top-level URDF entry point
│   └── joint_model.macro.urdf.xacro     # Xacro macro defining links and joints
├── package.xml
├── setup.py
└── setup.cfg
```

---

## Robot Model

The URDF model consists of the following links and joints:

| Link | Description |
|---|---|
| `world` | Fixed world frame |
| `base_link` | Base of the robot, fixed to the world |
| `stator_link` | The motor body (black box, 102×102×102 mm) |
| `rotor_link` | The rotating disc (red cylinder, r=25mm) |
| `angle_link` | Small white indicator bar showing rotor angle |

| Joint | Type | Description |
|---|---|---|
| `base_joint` | fixed | Connects world to base_link |
| `stator_joint` | fixed | Connects base_link to stator_link |
| `angle` | revolute | Rotating joint between stator and rotor (±π rad) |
| `indicator` | fixed | Connects rotor to angle indicator |

---

## Dependencies

- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `xacro`

---

## Usage

### Build the package

```bash
cd ~/ros2_ws
colcon build --packages-select joint_description
source install/setup.bash
```

### Launch the visualizer

```bash
ros2 launch joint_description view_model.launch.py
```

This will start:
- `robot_state_publisher` — publishes the robot model to `/robot_description`
- `joint_state_publisher_gui` — opens a GUI slider to manually control the rotor joint angle
- `rviz2` — opens RViz2 with the pre-configured `config.rviz` file

---

## Preview

Once launched, RViz2 will display the Qube model. Use the `joint_state_publisher_gui` slider to rotate the rotor and observe the angle indicator moving accordingly.
