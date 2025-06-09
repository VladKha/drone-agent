import os
import time
import numpy as np
import cv2
from dotenv import load_dotenv
from smolagents import tool
from djitellopy import Tello

from drone_agent.tools.TelloMock import TelloMock


load_dotenv()

IS_VIRTUAL = os.getenv('IS_VIRTUAL', False) == 'True'
SNAPSHOT_NUMBER = 0
IMAGES_DIR = 'images'

MOVEMENT_MIN = 20
MOVEMENT_MAX = 300
SCENE_CHANGE_DISTANCE = 120
SCENE_CHANGE_ANGLE = 90
MOVEMENT_X_ACCUMULATOR = 0
MOVEMENT_Y_ACCUMULATOR = 0
ROTATION_ACCUMULATOR = 0


print(f"Drone IS_VIRTUAL: {IS_VIRTUAL}")
if IS_VIRTUAL:
    drone = TelloMock()
else:
    drone = Tello()

drone.connect()
drone.streamon()  # start the video stream


@tool
def takeoff() -> str:
    """
    Take off the drone from the ground if the battery is good.
    If the battery is too low, the drone will not take off.
    Return a message indicating the result of the takeoff.

    Args:

    Returns:
        str: confirmation message "Drone took off" or "Battery is too low, drone cannot take off"

    Example:
        >>> result = takeoff()
        >>> print(result) # "Drone took off" or "Battery is too low, drone cannot take off"
    """
    if not is_battery_good():
        return 'Battery is too low, drone cannot take off'
    else:
        drone.takeoff()
        return "Drone took off"

@tool
def land() -> str:
    """
    Land the drone on the ground at the current location.
    Return a message indicating the result of the landing.

    Args:

    Returns:
        str: confirmation message "Drone landed" or "Drone cannot land, battery is too low"

    Example:
        >>> result = land()
        >>> print(result) # "Drone landed"
    """
    drone.land()
    return "Drone landed"


def adjust_exposure(img, alpha=1.0, beta=0):
    """
    Adjust the exposure of an image.

    :param img: Input image
    :param alpha: Contrast control (1.0-3.0). Higher values increase exposure.
    :param beta: Brightness control (0-100). Higher values add brightness.
    :return: Exposure adjusted image
    """
    # Apply exposure adjustment using the formula: new_img = img * alpha + beta
    new_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return new_img


def sharpen_image(img):
    """
    Apply a sharpening filter to an image.

    :param img: Input image
    :return: Sharpened image
    """
    # Define a sharpening kernel
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    # Apply the sharpening filter
    sharpened = cv2.filter2D(img, -1, kernel)
    return sharpened

@tool
def take_picture() -> np.ndarray:
    """
    Take a picture with the drone's camera.
    Return a message indicating the result of the picture.

    Args:

    Returns:
        np.ndarray: the image taken by the drone's camera

    Example:
        >>> result = take_picture()
        >>> print(result) # the image taken by the drone's camera
    """
    global SNAPSHOT_NUMBER

    frame = drone.get_frame_read().frame

    # adjust picture
    # frame = adjust_exposure(frame, alpha=1.3, beta=-30)
    # frame = sharpen_image(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB

    SNAPSHOT_NUMBER += 1
    os.makedirs(IMAGES_DIR, exist_ok=True)
    img_path = f'{IMAGES_DIR}/{SNAPSHOT_NUMBER}.jpg'
    cv2.imwrite(img_path, frame)

    print(f"Picture saved to {img_path}")
    return frame

def cap_distance(distance):
    if distance < MOVEMENT_MIN:
        return MOVEMENT_MIN
    elif distance > MOVEMENT_MAX:
        return MOVEMENT_MAX
    return distance

@tool
def move_forward(distance: int) -> str:
    """
    Move the drone forward by a given distance in centimeters.
    Return a message indicating the result of the movement.

    Args:
        distance (int): the distance to move forward in centimeters

    Returns:
        str: confirmation message "Drone moved forward by " + str(distance) + " cm"

    Example:
        >>> result = move_forward(100)
        >>> print(result) # "Drone moved forward by 100 cm"
    """
    global MOVEMENT_X_ACCUMULATOR

    drone.move_forward(cap_distance(distance))
    MOVEMENT_X_ACCUMULATOR += distance
    time.sleep(0.5)
    return "Drone moved forward by " + str(distance) + " cm"

@tool
def move_backward(distance: int) -> str:
    """
    Move the drone backward by a given distance in centimeters.
    Return a message indicating the result of the movement.

    Args:
        distance (int): the distance to move backward in centimeters

    Returns:
        str: confirmation message "Drone moved backward by " + str(distance) + " cm"

    Example:
        >>> result = move_backward(100)
        >>> print(result) # "Drone moved backward by 100 cm"
    """
    global MOVEMENT_X_ACCUMULATOR

    drone.move_back(cap_distance(distance))
    MOVEMENT_X_ACCUMULATOR -= distance
    time.sleep(0.5)
    return "Drone moved backward by " + str(distance) + " cm"

@tool
def move_left(distance: int) -> str:
    """
    Move the drone left by a given distance in centimeters.
    Return a message indicating the result of the movement.

    Args:
        distance (int): the distance to move left in centimeters

    Returns:
        str: confirmation message "Drone moved left by " + str(distance) + " cm"

    Example:
        >>> result = move_left(100)
        >>> print(result) # "Drone moved left by 100 cm"
    """
    global MOVEMENT_Y_ACCUMULATOR

    drone.move_left(cap_distance(distance))
    MOVEMENT_Y_ACCUMULATOR += distance
    time.sleep(0.5)
    return "Drone moved left by " + str(distance) + " cm"

@tool
def move_right(distance: int) -> str:
    """
    Move the drone right by a given distance in centimeters.
    Return a message indicating the result of the movement.

    Args:
        distance (int): the distance to move right in centimeters

    Returns:
        str: confirmation message "Drone moved right by " + str(distance) + " cm"

    Example:
        >>> result = move_right(100)
        >>> print(result) # "Drone moved right by 100 cm"
    """
    global MOVEMENT_Y_ACCUMULATOR

    drone.move_right(cap_distance(distance))
    MOVEMENT_Y_ACCUMULATOR -= distance
    time.sleep(0.5)
    return "Drone moved right by " + str(distance) + " cm"

@tool
def move_up(distance: int) -> str:
    """
    Move the drone up by a given distance in centimeters.
    Return a message indicating the result of the movement.

    Args:
        distance (int): the distance to move up in centimeters

    Returns:
        str: confirmation message "Drone moved up by " + str(distance) + " cm"

    Example:
        >>> result = move_up(100)
        >>> print(result) # "Drone moved up by 100 cm"
    """
    drone.move_up(cap_distance(distance))
    time.sleep(0.5)
    return "Drone moved up by " + str(distance) + " cm"

@tool
def move_down(distance: int) -> str:
    """
    Move the drone down by a given distance in centimeters.
    Return a message indicating the result of the movement.

    Args:
        distance (int): the distance to move down in centimeters

    """
    drone.move_down(cap_distance(distance))
    time.sleep(0.5)
    return "Drone moved down by " + str(distance) + " cm"

@tool
def turn_left(degree: int) -> str:
    """
    Turn the drone left by a given degree.
    Return a message indicating the result of the movement.

    Args:
        degree (int): the degree to turn left

    Returns:
        str: confirmation message "Drone turned left by " + str(degree) + " degrees"

    Example:
        >>> result = turn_left(90)
        >>> print(result) # "Drone turned left by 90 degrees"
    """
    global ROTATION_ACCUMULATOR

    drone.rotate_counter_clockwise(degree)
    ROTATION_ACCUMULATOR += degree
    time.sleep(1)
    return "Drone turned left by " + str(degree) + " degrees"

@tool
def turn_right(degree: int) -> str:
    """
    Turn the drone right by a given degree.
    Return a message indicating the result of the movement.

    Args:
        degree (int): the degree to turn right

    Returns:
        str: confirmation message "Drone turned right by " + str(degree) + " degrees"

    Example:
        >>> result = turn_right(90)
        >>> print(result) # "Drone turned right by 90 degrees"
    """
    global ROTATION_ACCUMULATOR

    drone.rotate_clockwise(degree)
    ROTATION_ACCUMULATOR -= degree
    time.sleep(1)
    return "Drone turned right by " + str(degree) + " degrees"

# TODO: return home?

def is_battery_good() -> bool:
    if IS_VIRTUAL:
        return True

    battery = drone.query_battery()
    print(f"Battery level: {battery}% ", end='')
    if battery < 20:
        print('is too low [WARNING]')
    else:
        print('[OK]')
        return True
    return False

def get_battery() -> str:
    battery = drone.get_battery()
    return f"Battery level: {battery}%"
