#!/usr/bin/env python3
import rospy
import click
import numpy as np
from std_msgs.msg import Float64MultiArray

# Function to strictly maintain vector consistency: 1x5000 double row vector
def format_sensor_data(sensor_value):
    # Create a 1x5000 array initialized to zeros
    data_vector = np.zeros((1, 5000), dtype=np.float64)
    # Store the actual sensor reading in the first index
    data_vector[0, 0] = sensor_value
    return data_vector

@click.command()
@click.option('--mode', default='simulation', help='Run mode: physical or simulation')
@click.option('--max-temp', default=25.0, help='Maximum temperature threshold')
def monitor_node(mode, max_temp):
    # Initialize the ROS node
    rospy.init_node('environment_monitor', anonymous=True)
    
    # Create publishers for Temperature and Humidity topics
    temp_pub = rospy.Publisher('/temperature', Float64MultiArray, queue_size=10)
    hum_pub = rospy.Publisher('/humidity', Float64MultiArray, queue_size=10)
    
    rate = rospy.Rate(1) # 1 Hz (Publishes once per second)
    
    rospy.loginfo(f"Starting environment monitor in {mode} mode.")
    rospy.loginfo(f"Temperature threshold limit set to {max_temp} C.")
    
    while not rospy.is_shutdown():
        # Simulate both sensors (Temperature and Humidity)
        current_temp = 20.0 + (np.random.rand() * 10.0) # Generates between 20.0C and 30.0C
        current_hum = 40.0 + (np.random.rand() * 20.0)  # Generates between 40.0% and 60.0%
        
        # Perform the required threshold monitoring
        if current_temp > max_temp:
            rospy.logwarn(f"WARNING: Temperature ({current_temp:.2f} C) has exceeded the {max_temp} C threshold!")
        
        # Apply the required vector formatting to both
        vectorized_temp = format_sensor_data(current_temp)
        vectorized_hum = format_sensor_data(current_hum)
        
        # Prepare ROS messages
        msg_temp = Float64MultiArray(data=vectorized_temp.flatten().tolist())
        msg_hum = Float64MultiArray(data=vectorized_hum.flatten().tolist())
        
        # Publish the data to the ROS network
        temp_pub.publish(msg_temp)
        hum_pub.publish(msg_hum)
        
        rate.sleep()

if __name__ == '__main__':
    try:
        monitor_node()
    except rospy.ROSInterruptException:
        pass
