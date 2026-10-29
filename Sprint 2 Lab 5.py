import time
import cv2
import threading
from pathlib import Path
from easytello import Tello

# Initialize Tello drone
myDrone = Tello()
myDrone.streamon()

# --- FILE PATH SETUP ---
# Get the directory where this current Python script is saved
current_directory = Path(__file__).resolve().parent#

# Define video file name and combine it with the script's directory
output_filename = f"tello_video_{int(time.time())}.mp4"
output_path = current_directory / output_filename
print(f"Video will be saved to: {output_path}")

# Define video format parameters
frame_width = 960
frame_height = 720
fps = 30

# Create VideoWriter object using the full absolute path string

#this file format would NOT work on the windows laptops
codec = cv2.VideoWriter.fourcc(*'mp4v')
video_writer = cv2.VideoWriter(str(output_path), codec, fps, (frame_width, frame_height))

# Control flag for the video thread
is_recording = True

def record_video():
    """Background thread function to continuously read and save video frames."""
    global is_recording
    print(f"Recording started. Press 'q' in the video window to stop early.")
    
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

    # Release resources when done
    video_writer.release()
    cv2.destroyAllWindows()

#Start the video recording in a separate background thread
video_thread = threading.Thread(target=record_video)
video_thread.start()


#****************************************************************************
try:
    # Main thread handles flight commands while video records concurrently
    # Put your comments and flight commands here:
    

    myDrone.takeoff()
    
    
   
    myDrone.land()

except Exception as e:
    print(f"An error occurred during flight: {e}")
    myDrone.land() # Safety fallback to land if something goes wrong

#Clean up and shut down
is_recording = False
video_thread.join() # Wait for the video thread to finish writing

myDrone.streamoff()
myDrone.end()

print(f"Video recording stopped and saved successfully to:\n{output_path}")
