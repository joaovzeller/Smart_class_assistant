#!/usr/bin/env python3
"""
ROS Noetic Node for Task 2: Attendance Management System
Author: Member 4
Description: Subscribes to /face_recognition/result, deduplicates student logs in RAM, 
             and writes verified check-ins directly to a local, persistent CSV log sheet.
"""

import os
import rospy
from datetime import datetime
from std_msgs.msg import String

class AttendanceNode:
    def __init__(self):
        rospy.init_node('attendance_node', anonymous=True)
        
        # Select target logging file path configuration
        package_path = os.path.dirname(os.path.realpath(__file__))
        self.csv_path = rospy.get_param('~log_file_path', os.path.join(package_path, "attendance_logs.csv"))
        
        # Deduplication cache to prevent multiple log records for the same occupant
        self.checked_in_students = set()
        
        self.initialize_database()

        # ROS Communication Setup
        self.status_pub = rospy.Publisher('/attendance/status', String, queue_size=10)
        self.result_sub = rospy.Subscriber('/face_recognition/result', String, self.process_result)
        
        rospy.loginfo(f"[AttendanceNode] Monitoring active. Appending entries to: {self.csv_path}")

    def initialize_database(self):
        """Prepares database schema layout with clean data column labels."""
        if not os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, 'w') as f:
                    f.write("Timestamp,Name,Role,Status\n")
                rospy.loginfo("[AttendanceNode] Initialized brand-new attendance CSV spreadsheet database.")
            except Exception as e:
                rospy.logerr(f"[AttendanceNode] Failed writing structural file headings: {e}")

    def process_result(self, msg):
        """Verifies parsed user identity streams and commits student logs to disk."""
        try:
            payload = msg.data
            if ":" not in payload:
                return
            
            name, role = payload.split(":", 1)

            # Restrict attendance logging specifically to Student profiles
            if role.strip().lower() == "student" and name != "Unknown":
                name_key = name.strip()
                
                # Verify that this student has not checked in during this session
                if name_key not in self.checked_in_students:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    self.write_record_to_csv(timestamp, name_key, "Student", "Present")
                    
                    self.checked_in_students.add(name_key)
                    
                    # Notify other nodes of a successful log operation
                    success_msg = f"SUCCESS:{name_key} logged at {timestamp}"
                    self.status_pub.publish(success_msg)
                    rospy.loginfo(f"[AttendanceNode] Check-In Success: {name_key}")

        except Exception as e:
            rospy.logerr(f"[AttendanceNode] Error processing incoming metadata packet: {e}")

    def write_record_to_csv(self, timestamp, name, role, status):
        """Appends formatted records to local storage disk."""
        try:
            with open(self.csv_path, 'a') as f:
                f.write(f"{timestamp},{name},{role},{status}\n")
        except IOError as e:
            rospy.logerr(f"[AttendanceNode] Disk IO failure logging data to path: {e}")

if __name__ == '__main__':
    try:
        node = AttendanceNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass