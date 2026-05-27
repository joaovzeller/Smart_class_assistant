#include <ros/ros.h>
#include <std_msgs/Bool.h>
#include <std_msgs/Int32.h>
#include <algorithm> // For std::max and std::min

class SmartLightingController {
private:
    ros::NodeHandle nh_;
    ros::Subscriber sub_motion_;
    ros::Subscriber sub_light_;
    ros::Publisher pub_light_cmd_;

    // Encapsulated State Variables
    bool room_active_;
    float smoothed_ambient_light_;
    
    // Configurable ROS Parameters
    int max_led_brightness_;
    float smoothing_factor_; 

public:
    SmartLightingController(ros::NodeHandle& nh) : nh_(nh), room_active_(false), smoothed_ambient_light_(50.0) {
        // Load parameters from the ROS server, with default fallbacks if they don't exist
        nh_.param("max_led_brightness", max_led_brightness_, 100);
        nh_.param("smoothing_factor", smoothing_factor_, 0.2f); // 0.0 to 1.0

        pub_light_cmd_ = nh_.advertise<std_msgs::Int32>("/command/led_brightness", 10);
        
        // Bind class methods to the ROS callbacks
        sub_motion_ = nh_.subscribe("/sensor/motion_detected", 10, &SmartLightingController::motionCallback, this);
        sub_light_ = nh_.subscribe("/sensor/ambient_light", 10, &SmartLightingController::lightCallback, this);
        
        ROS_INFO("Advanced OOP Lighting Controller Initialized.");
    }

    // Function 1: State Machine Toggle
    void motionCallback(const std_msgs::Bool::ConstPtr& msg) {
        if (msg->data && !room_active_) {
            ROS_INFO("Motion Edge Detected: Transitioning to ACTIVE state.");
        } else if (!msg->data && room_active_) {
            ROS_INFO("No Motion: Transitioning to STANDBY state.");
        }
        
        room_active_ = msg->data;
        updateLighting(); // Re-evaluate immediately upon state change
    }

    // Function 2: Signal Processing & Math
    void lightCallback(const std_msgs::Int32::ConstPtr& msg) {
        // Apply a Low-Pass Filter (Exponential Moving Average) to smooth noisy sensor input
        smoothed_ambient_light_ = (smoothing_factor_ * msg->data) + ((1.0 - smoothing_factor_) * smoothed_ambient_light_);
        updateLighting();
    }

    // Function 3: Command Execution and Clamping
    void updateLighting() {
        std_msgs::Int32 command_msg;
        
        if (!room_active_) {
            command_msg.data = 0; // Strict power saving
        } else {
            // Inverse proportional control
            int target = max_led_brightness_ - static_cast<int>(smoothed_ambient_light_);
            
            // Clamp the data to ensure we never output dangerous/invalid values to the hardware -0 to 100%
            command_msg.data = std::max(0, std::min(target, max_led_brightness_)); 
        }
        
        // Use ROS_INFO_THROTTLE so we don't spam the terminal 10 times a second
        ROS_INFO_
THROTTLE(2.0, "Ambient (Smoothed): %.1f%% | Target LED: %d%%", smoothed_ambient_light_, command_msg.data);
        
        pub_light_cmd_.publish(command_msg);
    }
};
int main(int argc, char **argv) {
    // Initialize the ROS system
    ros::init(argc, argv, "advanced_lighting_node");
    
    // Use a private node handle ("~") to access parameters specific to this node
    ros::NodeHandle nh("~"); 
    
    // Instantiate the class
    SmartLightingController controller(nh);
    
    // Hand execution over to ROS
    ros::spin();
    
    return 0;
}
