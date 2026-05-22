#!/usr/bin/env python3
import rospy
from std_msgs.msg import Bool, Int32
import click

@click.command()
@click.option('--motion', type=bool, default=False, help='Simulate motion detection (True/False)')
@click.option('--light', type=int, default=50, help='Simulate ambient light level (0-100)')
def inject_sensor_data(motion, light):
    # Initialize the ROS Node
    rospy.init_node('mock_sensor_injector', anonymous=True)

    # Create Publishers
    motion_pub = rospy.Publisher('/sensor/motion_detected', Bool, queue_size=10)
    light_pub = rospy.Publisher('/sensor/ambient_light', Int32, queue_size=10)

    # Wait a moment for connections to establish
    rospy.sleep(1)

    # Publish the data
    motion_pub.publish(motion)
    light_pub.publish(light)

    click.echo(f"Data Injected -> Motion: {motion} | Ambient Light: {light}%")

if __name__ == '__main__':
    try:
        inject_sensor_data()
    except rospy.ROSInterruptException:
        pass
