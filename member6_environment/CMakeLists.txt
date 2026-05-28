cmake_minimum_required(VERSION 3.0.2)
project(member6_environment)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/environment_monitor_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
