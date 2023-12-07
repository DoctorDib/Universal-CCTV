import cv2

# Specify the video source (0 for default camera)
video_source = 0

# Set up capture object
cap = cv2.VideoCapture(video_source)

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30  # Adjust the frames per second as needed

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter('output_video.mp4', fourcc, fps, (width, height))

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Break the loop if the video source has no more frames
    if not ret:
        break

    # Display the frame
    cv2.imshow('Frame', frame)

    # Write the frame to the output video file
    out.write(frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and writer objects
cap.release()
out.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
