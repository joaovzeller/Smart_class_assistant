class ClassroomManager:

    def __init__(self):

        self.system_active = False

        print("Smart Classroom Manager Started")

        self.publish_status("WAITING_FOR_ACTIVITY")

    def motion_callback(self, motion_detected):

        if motion_detected:

            print("Motion detected!")

            self.system_active = True

            self.publish_status("CLASSROOM_ACTIVE")

        else:

            print("No motion")

            self.system_active = False

            self.publish_status("CLASSROOM_IDLE")

    def publish_status(self, status):

        print(f"Classroom Status: {status}")


if __name__ == '__main__':

    manager = ClassroomManager()

    # Simulated sensor testing
    manager.motion_callback(True)

    manager.motion_callback(False)