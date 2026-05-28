#!/usr/bin/env python3
"""
Software Engineering for Robotics - Smart Classroom Project
Member 5: Speaker Tracking & Servo Control
Task 2: Camera Servo Motor Tracking Node
"""

import rclpy
from rclpy.node import Node
import tf2_ros
import math
import click

class ServoControllerNode(Node):
    def __init__(self, deadzone: float):
        super().__init__('servo_controller_node')
        self.deadzone = deadzone 
        
        # Instantiate coordinate stream tracking listeners
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        # High frequency execution sequence managing kinematics loops (20Hz)
        self.timer = self.create_timer(0.05, self.track_speaker)
        self.get_logger().info(f"Servo Node active. Filtering Deadzone config: {self.deadzone} rad.")

    def track_speaker(self):
        """Inspects dynamic space deviations and updates tracking trajectory targets."""
        try:
            now = rclpy.time.Time()
            transform = self.tf_buffer.lookup_transform('camera_link', 'speaker_frame', now)
            
            x = transform.transform.translation.x
            y = transform.transform.translation.y
            z = transform.transform.translation.z

            # Run inverse kinematics trigonometry transformations
            pan_angle = math.atan2(y, x)
            tilt_angle = math.atan2(z, x)

            # Jitter threshold check
            if abs(pan_angle) > self.deadzone:
                self.move_servos(pan_angle, tilt_angle)

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            pass # Suppress frame synchronization initialization delay outputs

    def move_servos(self, pan, tilt):
        """Converts coordinate orientation targets into hardware motor commands."""
        pan_deg = math.degrees(pan) + 90.0
        tilt_deg = math.degrees(tilt) + 90.0
        
        # Cap positions safely inside physical 0-180 limits
        pan_deg = max(0.0, min(180.0, pan_deg))
        tilt_deg = max(0.0, min(180.0, tilt_deg))
        
        self.get_logger().info(f"Servo Update Target -> Pan: {pan_deg:.1f}° | Tilt: {tilt_deg:.1f}°")


@click.command()
@click.option('--deadzone', default=0.05, help='Angular movement deadzone limit threshold in radians.')
def main(deadzone):
    """Advanced CLI parser setup hook configuration."""
    rclpy.init()
    node = ServoControllerNode(deadzone=deadzone)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Terminating Servo Node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()