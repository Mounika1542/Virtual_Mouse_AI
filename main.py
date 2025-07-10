import cv2
import mediapipe as mp
import pyautogui
import time
import datetime  # For timestamp

# Initialize video capture and hand detection
cap = cv2.VideoCapture(0)
hand_detector = mp.solutions.hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
index_x, index_y = 0, 0  # Initialize index_x and index_y
clicking = False
scrolling = False  # Track scrolling action

# Threshold for hand height to trigger screenshot
SCREENSHOT_HEIGHT_THRESHOLD = 0.3  # Adjust this value based on your setup

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Flip the frame for mirror effect
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark

            # Get the coordinates of the wrist (landmark 0)
            wrist = landmarks[0]
            wrist_y = int(wrist.y * frame_height)

            # Draw a circle around the wrist
            cv2.circle(img=frame, center=(int(wrist.x * frame_width), wrist_y), radius=10, color=(0, 255, 255))

            # Check if the hand is raised above the threshold for screenshot
            if wrist_y < frame_height * SCREENSHOT_HEIGHT_THRESHOLD:
                # Generate a unique filename using the current timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"screenshot_{timestamp}.png"
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_filename)  # Save the screenshot with a unique name
                print(f"Screenshot saved as {screenshot_filename}")  # Optional: Print the filename
                time.sleep(1)  # Prevent multiple screenshots

            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)

                if id == 8:  # Index finger tip
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                    index_x = screen_width / frame_width * x
                    index_y = screen_height / frame_height * y
                    pyautogui.moveTo(index_x, index_y)  # Move cursor based on index finger

                if id == 4:  # Thumb tip
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                    thumb_x = screen_width / frame_width * x
                    thumb_y = screen_height / frame_height * y

                    # Left click if thumb and index finger are close enough
                    distance = ((index_x - thumb_x)*2 + (index_y - thumb_y)*2)*0.5  # Euclidean distance
                    if distance < 50:  # Adjust this threshold for clicking gesture
                        if not clicking:
                            pyautogui.click()
                            clicking = True
                            time.sleep(0.2)  # Prevent multiple clicks
                    else:
                        clicking = False

                    # Right-click if thumb is far from index finger horizontally
                    if abs(index_x - thumb_x) > 50 and abs(index_y - thumb_y) < 30:
                        pyautogui.rightClick()

                # Scroll up if index finger is above thumb (Vertical distance based scroll)
                if id == 8 and index_y < thumb_y - 30:  # Finger above thumb (scroll up)
                    if not scrolling:
                        pyautogui.scroll(10)  # Scroll up
                        scrolling = True
                # Scroll down if index finger is below thumb (Vertical distance based scroll)
                elif id == 8 and index_y > thumb_y + 30:  # Finger below thumb (scroll down)
                    if not scrolling:
                        pyautogui.scroll(-10)  # Scroll down
                        scrolling = True
                else:
                    scrolling = False  # Reset scrolling if neither up nor down

            # Close folder if thumb is raised high (alt + f4)
            if thumb_y < 100:  # Adjust this threshold as needed
                pyautogui.hotkey('alt', 'f4')  # Use Alt + F4 to close the active window

            # Refresh page if index finger is pointed up
            if index_y < 100:  # Adjust this threshold as needed
                pyautogui.press('f5')

    cv2.imshow('Virtual Mouse with Screenshot', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
