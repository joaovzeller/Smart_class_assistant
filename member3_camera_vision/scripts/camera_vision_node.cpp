/**
 * ROS Noetic Node: Camera Integration & Face Detection
 * Member 3 - Advanced C++ Implementation
 * - Native C++ (roscpp) infrastructure
 * - Advanced command-line argument configuration inputs
 * - Dual ROS Functions: Camera Publishing & Haar Face Box Detection
 */

#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <geometry_msgs/Polygon.h>
#include <geometry_msgs/Point32.h>
#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include <opencv2/opencv.hpp>
#include <opencv2/objdetect.hpp>
#include <iostream>
#include <string>

class CameraVisionNode {
private:
    ros::NodeHandle nh_;
    ros::NodeHandle pnh_;
    
    // Communication channels
    ros::Publisher image_pub_;
    ros::Publisher face_pub_;
    
    // Hardware and tracking parameters
    cv::VideoCapture cap_;
    cv::CascadeClassifier face_cascade_;
    
    int camera_index_;
    bool visual_debug_;

public:
    CameraVisionNode(int camera_index, bool visual_debug) 
        : pnh_("~"), camera_index_(camera_index), visual_debug_(visual_debug) {
        
        // Resolve parameter server overrides fallback matching your CLI parameters
        pnh_.param("camera_index", camera_index_, camera_index_);
        pnh_.param("visual_debug", visual_debug_, visual_debug_);

        // Load OpenCV's pre-trained face cascade detection models
        // Standard Ubuntu paths for Haar datasets
        std::string cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml";
        if (!face_cascade_.load(cascade_path)) {
            ROS_ERROR("Critical: Failed to load Haar Cascade XML face tracking weights.");
            ros::shutdown();
        }

        // Task 1: Initialize Camera Node Stream Channel (Feeds Member 4)
        image_pub_ = nh_.advertise<sensor_msgs::Image>("/camera/image_raw", 10);

        // Task 2: Initialize Face Coordinate Polygon Channel (Feeds Member 5)
        face_pub = nh_.advertise<geometry_msgs::Polygon>("/camera/face_coordinates", 10);

        // Access target hardware camera stream
        cap_.open(camera_index_);
        if (!cap_.isOpened()) {
            ROS_ERROR("Hardware Failure: Could not link video capture loop index: %d", camera_index_);
            ros::shutdown();
        }

        ROS_INFO("C++ Vision Node Online. Device Index: %d | GUI Panel: %s", 
                 camera_index_, visual_debug_ ? "ENABLED" : "DISABLED");
    }

    void spinPipeline() {
        ros::Rate rate(20); // Maintain a stable 20Hz runtime processing threshold
        cv::Mat frame, gray_frame;

        while (ros::ok()) {
            cap_ >> frame;
            if (frame.empty()) {
                ROS_WARN("Vision pipeline frame dropped from camera feed. Resampling...");
                ros::spinOnce();
                rate.sleep();
                continue;
            }

            // --- Task 1: Frame Translation via CvBridge ---
            try {
                std::string encoding = "bgr8";
                sensor_msgs::ImagePtr msg = cv_bridge::CvImage(std_msgs::Header(), encoding, frame).toImageMsg();
                image_pub_.publish(msg);
            }
            catch (cv_bridge::Exception& e) {
                ROS_ERROR("CvBridge compilation error trap handled: %s", e.what());
            }

            // --- Task 2: Face Detection Logic Loop ---
            cv::cvtColor(frame, gray_frame, cv::COLOR_BGR2GRAY);
            std::vector<cv::Rect> faces;
            
            // Analyze pixels for match metrics
            face_cascade_.detectMultiScale(gray_frame, faces, 1.2, 5, 0, cv::Size(40, 40));

            geometry_msgs::Polygon face_polygon;
            for (size_t i = 0; i < faces.size(); ++i) {
                // Populate structural geometric boundary point arrays
                geometry_msgs::Point32 p1, p2;
                p1.x = faces[i].x;
                p1.y = faces[i].y;
                p2.x = faces[i].x + faces[i].width;
                p2.y = faces[i].y + faces[i].height;

                face_polygon.points.push_back(p1);
                face_polygon.points.push_back(p2);

                if (visual_debug_) {
                    cv::rectangle(frame, faces[i], cv::Scalar(0, 255, 0), 2);
                }
            }

            // Route tracked coordinates to Member 5's servo nodes
            if (!faces.empty()) {
                face_pub_.publish(face_polygon);
            }

            // Handle tracking debug rendering options
            if (visual_debug_) {
                cv::imshow("Member 3 - C++ Vision Verification Window", frame);
                if (cv::waitKey(1) == 'q') {
                    break;
                }
            }

            ros::spinOnce();
            rate.sleep();
        }
        cv::destroyAllWindows();
    }
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "camera_vision_node");

    // Standard CLI processing implementation for C++
    int target_index = 0;
    bool enable_gui = true;

    // Advanced manual parsing checking for flags like --no-gui or --index passed down to terminal
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--no-gui") {
            enable_gui = false;
        } else if (arg == "--index" && i + 1 < argc) {
            target_index = std::atoi(argv[++i]);
        }
    }

    CameraVisionNode node(target_index, enable_gui);
    node.spinPipeline();
    return 0;
}
