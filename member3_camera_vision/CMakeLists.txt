cmake_minimum_required(VERSION 3.0.2)
project(member3_camera_vision)

find_package(catkin REQUIRED COMPONENTS
  rospy
  sensor_msgs
  geometry_msgs
  cv_bridge
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/camera_vision_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
