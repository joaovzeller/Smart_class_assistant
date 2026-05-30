#!/usr/bin/env python3
"""
PyTest Framework Integration File for Vision Nodes
"""

import sys
import pytest
import rospy
import time
import subprocess
from sensor_msgs.msg import Image
from geometry_msgs.msg import Polygon

@pytest.fixture(scope="module")
def ros_test_env():
    """Initializes the ROS test node network context."""
    rospy.init_node('pytest_cpp_vision_validator', anonymous=True)
    
    # This feeds --no-gui to the CLI to prevent display windows from blocking server tests
    cpp_node_cmd = ["rosrun", "member3_camera_vision", "camera_vision_node", "--no-gui"]
    process = subprocess.Popen(cpp_node_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give the C++ binary a brief window to initialize its hardware cap links
    time.sleep(2.0)
    
    yield process
    
    # Teardown: Safely terminate the C++ node process after tests finish
    process.terminate()
    process.wait()

def test_cpp_stream_delivery_to_member4(ros_test_env):
    """
    Validates that the compiled C++ node successfully publishes raw images 
    to the exact topic channel Member 4 uses for face recognition.
    """
    frames_intercepted = []

    def image_callback(msg):
        frames_intercepted.append(msg)

    # Subscribe to the C++ node's image output channel
    rospy.Subscriber('/camera/image_raw', Image, image_callback)
    
    # Monitor the topic for a few seconds to intercept incoming data matrices
    timeout = time.time() + 4.0
    while len(frames_intercepted) == 0 and time.time() < timeout:
        time.sleep(0.1)

    # Assert structural compliance: Did our C++ node send valid image envelopes?
    assert len(frames_intercepted) > 0, "Integration Break: C++ /camera/image_raw stream is offline."
    assert frames_intercepted[0].encoding == "bgr8", "Encoding Mismatch: Expected bgr8 format matrix."

def test_cpp_coordinates_delivery_to_member5(ros_test_env):
    """
    Validates that the C++ node creates the coordinate tracking structures 
    needed by Member 5's servo tracking nodes.
    """
    coordinates_intercepted = []

    def face_callback(msg):
        coordinates_intercepted.append(msg)

    # Subscribe to the geometric polygon topic published by your C++ node
    rospy.Subscriber('/camera/face_coordinates', Polygon, face_callback)
    
    # Give the system a brief moment to process the pipeline loop
    time.sleep(1.0)
    
    # Note: In a headless testing server without a real human face, this array may be empty.
    # We are testing that the topic exists and is registerable on the ROS master graph.
    assert '/camera/face_coordinates' in dict(rospy.get_published_topics()), "Topic path registration missing."
