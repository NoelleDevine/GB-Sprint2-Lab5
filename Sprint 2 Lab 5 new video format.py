import time
import cv2
import threading
from pathlib import Path
from easytello import Tello

# Initialize Tello drone
myDrone = Tello()
myDrone.streamon()
time.sleep(2)  # Give the video stream time to initialize

# --- FILE PATH SETUP ---
current_directory = Path(__file__).resolve().parent

# Use .avi and MJPG for reliable playback
output_filename = f"tello_video_{int(time.time())}.avi"
output_path = current_directory / output_filename
print(f"Video will be saved to: {output_path}")

# Define video format parameters
frame_width = 960
frame_height = 720
fps = 30

# Create VideoWriter object
codec = cv2.VideoWriter.fourcc(*'MJPG')
video_writer = cv2.VideoWriter(str(output_path), codec, fps, (frame_width, frame_height))

# Control flag for the video thread
is_recording = True

def record_video():
    """Background thread function to continuously read and save video frames."""
    global is_recording
    print("Recording started. Press 'q' in the video window to stop early.")
    
    while is_recording:
        try:
            frame = myDrone.get_frame_read().frame
            if frame is not None:
                frame = cv2.resize(frame, (frame_width, frame_height))
                video_writer.write(frame)
                cv2.imshow("Tello Video Feed", frame)
            
            # Allow quitting early via OpenCV window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                is_recording = False
                break
        except Exception as e:
            print(f"Error in video thread: {e}")
            break

    # Release resources properly so headers save correctly
    video_writer.release()
    cv2.destroyAllWindows()

# Start the video recording in a separate background thread
video_thread = threading.Thread(target=record_video)
video_thread.start()

# ****************************************************************************
try:
    myDrone.takeoff()
    
    # Add your flight movements here (e.g., myDrone.forward(50))
    
    myDrone.land()

except Exception as e:
    print(f"An error occurred during flight: {e}")
    myDrone.land()

# Clean up and shut down safely
is_recording = False
video_thread.join() # Wait for thread to finish and trigger video_writer.release()

myDrone.streamoff()
myDrone.end()

print(f"Video recording stopped and saved successfully to:\n{output_path}")