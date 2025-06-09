import cv2

class TelloMock:
    def __init__(self): pass

    def connect(self): pass

    def streamon(self):
        # Open the default camera (usually index 0)
        self.cap = cv2.VideoCapture(0)

    def takeoff(self): pass

    def land(self): pass

    def get_battery(self): pass

    def take_picture(self): pass

    def move_forward(self, distance: int): pass

    def move_back(self, distance: int): pass

    def move_left(self, distance: int): pass

    def move_right(self, distance: int): pass

    def move_up(self, distance: int): pass

    def move_down(self, distance: int): pass

    def rotate_counter_clockwise(self, degree: int): pass

    def rotate_clockwise(self, degree: int): pass

    def get_frame_read(self):
        cap = self.cap

        class DummyFrame:
            def __init__(self):
                _, frame = cap.read()
                self.frame = frame

                # Generate a simple random image
                # self.frame = np.random.randint(0, 255, (720, 960, 3), dtype=np.uint8)

        return DummyFrame()
