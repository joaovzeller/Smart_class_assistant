#!/usr/bin/env python3
"""
ROS Noetic Node: Camera Integration & Face Detection
Member 3 - Python Implementation with Click CLI
"""

import sys
import rospy
import click
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from geometry_msgs.msg import Polygon, Point32

class CameraVisionNode:
    def __init__(self, camera_index, visual_debug):
        rospy.init_node('camera_vision_node', anonymous=False)
        
        # Fallback parameters from the ROS parameter server or Click defaults
        self.camera_index = rospy.get_param('~camera_index', camera_index)
        self.visual_debug = rospy.get_param('~visual_debug', visual_debug)
        
        self.bridge = CvBridge()
        
        # Load OpenCV face detection weights
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Publishers that your teammate's C++ nodes can instantly read
        self.image_pub = rospy.Publisher('/camera/image_raw', Image, queue_size=10)
        self.face_pub = rospy.Publisher('/camera/face_coordinates', Polygon, queue_size=10)
        
        self.cap = cv2.VideoCapture(self.camera_index)
        rospy.loginfo(f"Python Vision Node Started. Index: {self.camera_index}")

    def run(self):
        rate = rospy.Rate(20) # 20 Hz loop rate
        while not rospy.is_shutdown():
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Publish raw images for Member 4's Python node
            try:
                ros_img = self.bridge.cv2_to_imgmsg(frame, "bgr8")
                self.image_pub.publish(ros_img)
            except CvBridgeError as e:
                rospy.logerr(e)

            # Detect faces for Member 5's C++ node
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(40, 40))

            face_polygon = Polygon()
            for (x, y, w, h) in faces:
                # Top-Left and Bottom-Right bounding vertices
                face_polygon.points.append(Point32(x=float(x), y=float(y), z=0.0))
                face_polygon.points.append(Point32(x=float(x+w), y=float(y+h), z=0.0))
                
                if self.visual_debug:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            if len(faces) > 0:
                self.face_pub.publish(face_polygon)

            if self.visual_debug:
                cv2.imshow("Member 3 - Python Window", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            rate.sleep()

        self.cap.release()
        cv2.destroyAllWindows()

# Advanced CLI Configuration via Click
@click.command()
@click.option('--index', default=0, type=int, help='Camera device index path.')
@click.option('--gui/--no-gui', default=True, help='Show video window stream display panel.')
def main(index, gui):
    # Strip ROS internal remap arguments before handing over to click
    sys.argv = rospy.myargv(argv=sys.argv)
    
    node = CameraVisionNode(camera_index=index, visual_debug=gui)
    node.run()

if __name__ == '__main__':
    main()
