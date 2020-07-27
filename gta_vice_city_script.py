import numpy as np
from PIL import ImageGrab
import pyautogui
import pydirectinput
import cv2

ENGINE_FIRE_LOW = (8, 83, 84)
ENGINE_FIRE_UP = (100, 255, 255)

FIND_ROAD_LANE_LOW = (20, 98, 100)
FIND_ROAD_LANE_UP = (30, 255, 255)

POLICE_STAR_LOW = (74, 100, 100)
POLICE_STAR_UP = (101, 255, 255)

ROAD_MEMORY = list()


def game_frame(target_frame):
    # Grab the desired region
    bbox = target_frame
    target_screen = np.array(ImageGrab.grab(bbox))
    return target_screen


def detect_engine_fire(screen, screen_hsv, screen_rgb):
    # Region of interest: engine region in the frame
    black_background = np.zeros((screen.shape[0], screen.shape[1], 3), np.uint8)
    roi_in_black = cv2.rectangle(black_background, (290, 100), (360, 300), (255, 255, 255), -1)
    gray = cv2.cvtColor(roi_in_black, cv2.COLOR_BGR2GRAY)
    _, roi_mask = cv2.threshold(gray, 127, 255, 0)

    # Decomposition of the fire color scale

    fire_mask = cv2.inRange(screen_hsv, ENGINE_FIRE_LOW, ENGINE_FIRE_UP)
    fire_mask = cv2.erode(fire_mask, None, iterations=2)
    fire_mask = cv2.dilate(fire_mask, None, iterations=2)
    engine_fire_in_roi = cv2.bitwise_and(fire_mask, fire_mask, mask=roi_mask)

    # Contouring the desired area

    contours, _ = cv2.findContours(engine_fire_in_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if contours:
        cnt = contours[0]
        cv2.drawContours(screen_rgb, cnt, -1, (0, 0, 255), 3)
        area = cv2.contourArea(cnt)
        print(area)
        if 2500 < area < 8000:
            pyautogui.write("ASPIRINE")


def detect_police_stars(screen, screen_hsv, screen_rgb):
    # Region of interest: the region of the police stars in the frame
    black_background = np.zeros((screen.shape[0], screen.shape[1], 3), np.uint8)
    roi_in_black_background = cv2.rectangle(black_background,
                                            (530, 58), (538, 65), (255, 255, 255), -1)
    gray = cv2.cvtColor(roi_in_black_background, cv2.COLOR_BGR2GRAY)
    _, roi_mask = cv2.threshold(gray, 127, 255, 0)

    # Decomposition of the active police stars color scale (like a cyan ~~)

    police_hsv_mask = cv2.inRange(screen_hsv, POLICE_STAR_LOW, POLICE_STAR_UP)
    police_stars_mask = cv2.bitwise_and(police_hsv_mask, police_hsv_mask, mask=roi_mask)

    # Contouring the desired area

    contours, _ = cv2.findContours(police_stars_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if contours:
        cnt = contours[0]
        cv2.drawContours(screen_rgb, cnt, -1, (0, 0, 255), 5)
        pyautogui.write("LEAVEMEALONE")


def detect_road_lanes(screen, screen_hsv, screen_rgb):
    # Region of interest: middle zone of frame
    black_background = np.zeros((screen.shape[0], screen.shape[1]), np.uint8)
    roi_corner_points = np.array([[(0, 300), (0, 100), (640, 100), (640, 300)]], dtype=np.int32)
    channel_count = screen.shape[2]
    mask_area_color = (255,) * channel_count
    cv2.fillPoly(black_background, roi_corner_points, mask_area_color)

    # Decomposition of road lane color scale

    road_lane_hsv_mask = cv2.inRange(screen_hsv, FIND_ROAD_LANE_LOW, FIND_ROAD_LANE_UP)
    road_lane_hsv_mask = cv2.erode(road_lane_hsv_mask, None, iterations=2)
    road_lane_hsv_mask = cv2.dilate(road_lane_hsv_mask, None, iterations=2)
    the_yellow_road_lane = cv2.bitwise_and(road_lane_hsv_mask,
                                           road_lane_hsv_mask, mask=black_background)

    # Contouring the desired area

    contours, _ = cv2.findContours(the_yellow_road_lane, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if contours:
        cnt = contours[0]
        cv2.drawContours(screen_rgb, cnt, -1, (0, 255, 0), 10)
        xxx, yyy = cnt[0][0]

        cv2.line(screen_rgb, (300, 400), (xxx, yyy), (255, 0, 0), 4)
        cv2.line(screen_rgb, (330, 400), (xxx, yyy), (255, 0, 0), 4)
        cv2.line(screen_rgb, (270, 400), (xxx, yyy), (255, 0, 0), 4)

        """ If the road lane disappears from the frame due to the bend, 
        the sequence that reminds the last position of the lane """

        ROAD_MEMORY.append(xxx)
        if len(ROAD_MEMORY) > 1:
            ROAD_MEMORY.pop(0)

        if xxx < 290:
            pydirectinput.keyUp("right")
            pydirectinput.keyDown("left")

        if xxx > 310:
            pydirectinput.keyUp("left")
            pydirectinput.keyDown("right")
    else:
        if ROAD_MEMORY:
            xxx = ROAD_MEMORY[0]
            if xxx < 250:
                pydirectinput.keyUp("right")
                pydirectinput.keyDown("left")

            if xxx > 380:
                pydirectinput.keyUp("left")
                pydirectinput.keyDown("right")


while True:

    SCREEN_ = game_frame((10, 40, 630, 470))

    # Processing of the received image

    SCREEN_RGB_ = cv2.cvtColor(SCREEN_, cv2.COLOR_BGR2RGB)
    SCREEN_BLURRED = cv2.GaussianBlur(SCREEN_, (11, 11), 0)
    SCREEN_HSV_ = cv2.cvtColor(SCREEN_BLURRED, cv2.COLOR_RGB2HSV)

    detect_engine_fire(SCREEN_, SCREEN_HSV_, SCREEN_RGB_)

    detect_police_stars(SCREEN_, SCREEN_HSV_, SCREEN_RGB_)

    detect_road_lanes(SCREEN_, SCREEN_HSV_, SCREEN_RGB_)

    # Lane tracking has started

    pydirectinput.keyUp("left")
    pydirectinput.keyUp("right")
    pyautogui.keyDown("w")

    cv2.imshow('GAME WINDOW', SCREEN_RGB_)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
