# GTA Vice City Script with OpenCV
  --------OpenCV projects on games--------

Script that: automatically escapes from the cops, stops the engine fire automatically and Tommy Vercetti  keeps following the lane 
## Usage
Set the game window to be in the upper left corner of the screen, to 640x480 and run the code. That's all

## OK. How is it working?

The real time frame is converted into hsv space

![hsv](https://user-images.githubusercontent.com/67822910/88494606-811bb000-cfbf-11ea-9f6e-771a5c737ff9.PNG)

Then it is masked by the color of the fire.

![hsv mask](https://user-images.githubusercontent.com/67822910/88494696-d0fa7700-cfbf-11ea-8766-e1e152fd2a50.PNG)

But there can be many regions in this color scale in the frame and we only need the region corresponding to the engine.
So it needs to be masked by a region of interest.

![engine fire mask](https://user-images.githubusercontent.com/67822910/88494259-eff80980-cfbd-11ea-8d22-19a682b53e76.PNG)
        
 There is the engine fire in this area in the frame. The following image is created after masking with this region. 
 
 ![the engine fire](https://user-images.githubusercontent.com/67822910/88494906-c55b8000-cfc0-11ea-9d06-5e16d69fb4b3.PNG)
 
 If the contour is found in the size set in this area, it is understood that there is a fire then cheat wrote.
 
 You can guess this cheat code :D
 The cheat: "ASPIRINE" 
 
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
            
 OK. Let's continue second part
 
 The default color is dark blue in the area where the police stars but when the cops chase us, this color turns into cyan-like.
 This time, we need to mask the hsv space with cyan. And after we should mask the region where the stars are located.
 
![police stars mask](https://user-images.githubusercontent.com/67822910/88495540-e1f8b780-cfc2-11ea-82d5-442604b5efe8.PNG)

I made this area very small because we have to get rid of it even if it is one star. Another reason is it should not process the sky with inaccuracy.
If a contour is found in this area, the following cheat is automatically written.

"LEAVEMEALONE"

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

Let's continue third part

In this part, Tommy Vercetti follows the yellow lines on the road. Since the game is old, the color transitions on the road lines are not understood enough. So it is difficult to have a road lane tracking on a car. 

I didn't use hough transform here because, as I said, the lines are not clear enough. So I use findcontours and I detect yellow lane at the middle of the road. If the strip disappears from the frame screen due to bend, its last position is kept in a list, the number of elements of the list is fixed as one, and when there is no strip on the screen, movement is provided according to this list.

![road lane tracking](https://user-images.githubusercontent.com/67822910/88496074-a2cb6600-cfc4-11ea-8e25-6505db6d05a3.PNG)
 
 I used the pyautogui library and Ben Johnson's pydirectinput library for checks and cheats.
 
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
 
 
 
