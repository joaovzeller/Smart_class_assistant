#!/usr/bin/env python3
"""
ROS Noetic Node for Task 1: Face Recognition System
Author: Member 4
Description: Subscribes to /camera/image_raw, identifies registered classroom faces 
             using the face_recognition library, and publishes "Name:Role" outputs.
"""

import os
import rospy
import cv2
import face_recognition
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import String

class FaceRecognitionNode:
    def __init__(self):
        # Register local node profile
        rospy.init_node('face_recognition_node', anonymous=True)
        self.bridge = CvBridge()
        
        # Locate reference directory containing images named 'Firstname_Lastname_Role.jpg'
        package_path = os.path.dirname(os.path.realpath(__file__))
        self.faces_dir = os.path.join(package_path, "faces")
        
        # Dynamic ROS parameter lookups
        self.tolerance = rospy.get_param('~recognition_tolerance', 0.6)
        self.resize_factor = rospy.get_param('~resize_factor', 0.25)
        
        self.known_face_encodings = []
        self.known_face_metadata = []
        
        # Parse face database configurations
        self.load_known_faces()
        
        # ROS communication hooks
        self.result_pub = rospy.Publisher('/face_recognition/result', String, queue_size=10)
        self.image_sub = rospy.Subscriber('/camera/image_raw', Image, self.image_callback)
        
        rospy.loginfo("[FaceRecognitionNode] Online and subscribing to /camera/image_raw.")

    def load_known_faces(self):
        """Loads reference faces named as Name_Role.jpg from the local database directory."""
        if not os.path.exists(self.faces_dir):
            rospy.logwarn(f"[FaceRecognitionNode] Directory '{self.faces_dir}' not found. Initializing empty folder.")
            os.makedirs(self.faces_dir)
            return

        for filename in os.listdir(self.faces_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(self.faces_dir, filename)
                try:
                    base_name, _ = os.path.splitext(filename)
                    if "_" in base_name:
                        name_part, role = base_name.rsplit("_", 1)
                    else:
                        name_part, role = base_name, "Unknown"

                    display_name = name_part.replace("_", " ")
                    image_matrix = face_recognition.load_image_file(filepath)
                    face_encodings = face_recognition.face_encodings(image_matrix)
                    
                    if len(face_encodings) > 0:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_metadata.append({"name": display_name, "role": role})
                        rospy.loginfo(f"[FaceRecognitionNode] Registered database profile: {display_name} ({role})")
                    else:
                        rospy.logwarn(f"[FaceRecognitionNode] No faces found in local file profile: {filename}")
                except Exception as e:
                    rospy.logerr(f"[FaceRecognitionNode] Could not read file {filename}: {str(e)}")

    def image_callback(self, msg):
        """Processes incoming video feeds, detects facial models, and registers classification results."""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as e:
            rospy.logerr(f"[FaceRecognitionNode] CvBridge failure processing stream frames: {e}")
            return

        # Downsample the matrix size to decrease execution pressure on low-power architectures
        small_frame = cv2.resize(cv_image, (0, 0), fx=self.resize_factor, fy=self.resize_factor)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=self.tolerance)
            name = "Unknown"
            role = "Unknown"

            if True in matches:
                matched_index = matches.index(True)
                name = self.known_face_metadata[matched_index]["name"]
                role = self.known_face_metadata[matched_index]["role"]

            # Output topic string payload
            payload = f"{name}:{role}"
            self.result_pub.publish(payload)

if __name__ == '__main__':
    try:
        node = FaceRecognitionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass