#!/usr/bin/env python3
"""
Software Engineering for Robotics - Smart Classroom Project
Member 5: Speaker Tracking & Servo Control
Task 1: Audio/Speaker Detection Node
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math
import click

class AudioProcessingNode(Node):
    def __init__(self, simulation_mode: bool):
        super().__init__('audio_processing_node')
        self.sim_mode = simulation_mode
        
        # Initialize the TF broadcaster to publish coordinate transforms
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        
        # Timer tracking audio direction processing updates at 10Hz
        self.timer = self.create_timer(0.1, self.detect_speaker_callback)
        self.get_logger().info(f"Audio Processing Node active. Sim Mode: {self.sim_mode}")
        
        self.sim_angle = 0.0

    def detect_speaker_callback(self):
        """Calculates audio direction-of-arrival and broadcasts it as a spatial frame."""
        if self.sim_mode:
            # Simulate a live human speaking while walking across the room (+/- 45 degrees)
            self.sim_angle += 0.05
            angle = math.sin(self.sim_angle) * 0.785  
            x = math.cos(angle) * 2.0                 
            y = math.sin(angle) * 2.0
            z = 0.0
        else:
            # Hardware hook placeholder: Integrate physical microphone array array data streams here
            x, y, z = 1.0, 0.0, 0.0 

        # Build structural coordinate transform message
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'camera_link'
        t.child_frame_id = 'speaker_frame'
        
        t.transform.translation.x = float(x)
        t.transform.translation.y = float(y)
        t.transform.translation.z = float(z)
        
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # Broadcast spatial position into global TF ecosystem
        self.tf_broadcaster.sendTransform(t)


@click.command()
@click.option('--sim', is_flag=True, help='Enables mock audio data emulation loop.')
def main(sim):
    """Advanced CLI endpoint parsing logic."""
    rclpy.init()
    node = AudioProcessingNode(simulation_mode=sim)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Terminating Audio Node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()