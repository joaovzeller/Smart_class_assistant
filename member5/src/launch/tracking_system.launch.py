from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Run Audio Processor
        Node(
            package='classroom_automation',
            executable='audio_processing_node',
            name='audio_processor_unit',
            output='screen',
            arguments=['--sim']
        ),
        # Run Target Servo Controller Tracking Unit
        Node(
            package='classroom_automation',
            executable='servo_controller_node',
            name='servo_actuator_unit',
            output='screen',
            arguments=['--deadzone', '0.04']
        )
    ])