cmake_minimum_required(VERSION 3.0.2)
project(member4_face_recognition)

# Locate essential catkin packages required for Member 4 package compilation
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  cv_bridge
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs sensor_msgs cv_bridge
)

# Mark the Python nodes as executable scripts to be installed correctly
catkin_install_python(PROGRAMS
  scripts/face_recognition_node.py
  scripts/attendance_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)