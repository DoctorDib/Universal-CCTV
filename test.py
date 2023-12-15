import cv2

def get_resolution(rotation, resolution):
    resolution = resolution.lower().split('x')
    if (rotation == 90 or rotation == 270):
        return [int(resolution[1]), int(resolution[0])]
    else:
        return [int(resolution[0]), int(resolution[1])]

# Specify the video source (0 for default camera)
video_source = 0
fps = 30  # Adjust the frames per second as needed
rotation = 90
resolution = "1920x1080"

# Set up capture object
cap = cv2.VideoCapture(video_source)
test = get_resolution(rotation, resolution)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, test[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, test[1])

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter('output_video.mp4', fourcc, fps, (test[0], test[1]))

while True:
    _, frame = cap.read()

    # Rotate image
    if (rotation == 90):
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == 180):
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif (rotation == 270):
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    

    # cv2.getRotationMatrix2D((test[0] / 2, test[1] / 2), 90, 1.0)

    # Get the height and width of the frame
    height, width, _ = frame.shape

    print("H: ", height)
    print("w: ", width)

    

    # Define the dimensions of the black bar
    bar_height = int(height / 20)  # You can adjust the height as needed
    bar_color = (0, 0, 0)  # Black color

    # Create a black bar at the top middle of the frame
    frame[0:bar_height, :] = bar_color

    font_scale = .5
    font_thickness = 1

    # Add text to the black bar
    text = "Test Footage"
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_x = int((width - text_size[0]) / 2)
    text_y = int(bar_height / 2) + int(text_size[1] / 2)
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

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



