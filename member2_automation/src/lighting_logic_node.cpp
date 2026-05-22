#include "ros/ros.h"
#include "std_msgs/Bool.h"
#include "std_msgs/Int32.h"

// Global variables to store state
bool room_active = false;
ros::Publisher light_cmd_pub;

// C++ Function 1: Handle Motion Data
void motionCallback(const std_msgs::Bool::ConstPtr& msg) {
    room_active = msg->data;
    if(room_active) {
        ROS_INFO("Motion detected. Classroom activated.");
    } else {
        ROS_INFO("No motion. Classroom deactivated.");
    }
}

// C++ Function 2: Handle Light Data and calculate output
void lightCallback(const std_msgs::Int32::ConstPtr& msg) {
    std_msgs::Int32 command_msg;

    if(!room_active) {
        command_msg.data = 0; // Lights off if room is empty
    } else {
        // Inverse lighting: If ambient is 20%, LEDs need to be 80%
        command_msg.data = 100 - msg->data; 
    }

    ROS_INFO("Ambient Light: %d%% | Adjusting Room LEDs to: %d%%", msg->data, command_msg.data);
    light_cmd_pub.publish(command_msg);
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "lighting_logic_node");
    ros::NodeHandle n;

    light_cmd_pub = n.advertise<std_msgs::Int32>("/command/led_brightness", 10);

    ros::Subscriber sub_motion = n.subscribe("/sensor/motion_detected", 10, motionCallback);
    ros::Subscriber sub_light = n.subscribe("/sensor/ambient_light", 10, lightCallback);

    ros::spin();
    return 0;
}
