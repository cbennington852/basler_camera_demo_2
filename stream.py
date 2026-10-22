import cv2
import numpy as np
from pypylon import pylon

# 1. Initialize and open the first found Basler camera
CAMERA_IP = "10.1.1.57" 

try:
    info = pylon.DeviceInfo()
    info.SetPropertyValue('IpAddress', CAMERA_IP)

    tl_factory = pylon.TlFactory.GetInstance()
    camera = pylon.InstantCamera(tl_factory.CreateFirstDevice(info))
    camera.Open()
    print(f"Connected to camera at {CAMERA_IP}")

    # -----------------------------------------------------------------
    # EXPOSURE CONFIGURATION
    # -----------------------------------------------------------------
    # 1. Turn off Auto Exposure so your manual value takes effect
    if hasattr(camera, 'ExposureAuto'):
        camera.ExposureAuto.SetValue('Off')
    
    # 2. Set the custom exposure value in MICROSECONDS (1000 µs = 1 ms)
    # Change 20000 to whatever value works best for your lighting
    target_exposure = 20000 
    
    if hasattr(camera, 'ExposureTime'):
        # Ensure the value is within the camera's physical hardware limits
        target_exposure = max(camera.ExposureTime.Min, min(target_exposure, camera.ExposureTime.Max))
        camera.ExposureTime.SetValue(target_exposure)
        print(f"Exposure set to: {camera.ExposureTime.GetValue()} µs")
    elif hasattr(camera, 'ExposureTimeAbs'):  # Fallback for older GigE models
        target_exposure = max(camera.ExposureTimeAbs.Min, min(target_exposure, camera.ExposureTimeAbs.Max))
        camera.ExposureTimeAbs.SetValue(target_exposure)
        print(f"Exposure set to: {camera.ExposureTimeAbs.GetValue()} µs")
    # -----------------------------------------------------------------

except Exception as e:
    print(f"Error: {e}")

# 2. Get camera frame properties for VideoWriter setup
# Adjust camera properties if needed (e.g., Target Frame Rate)
camera.AcquisitionFrameRateEnable.SetValue(True)
camera.AcquisitionFrameRateAbs.SetValue(30.0)  # Set desired PoE frame rate

width = camera.Width.GetValue()
height = camera.Height.GetValue()
fps = camera.AcquisitionFrameRateAbs.GetValue()

print(f"Connected to: {camera.GetDeviceInfo().GetModelName()}")
print(f"Resolution: {width}x{height} @ {fps} FPS")

# 3. Configure OpenCV VideoWriter for continuous recording
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter('output_poe_video.mp4', fourcc, fps, (width, height))

# 4. Prepare image converter to convert Basler format to OpenCV BGR
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# 5. Start grab loop using the Latest Image Strategy to minimize latency
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

try:
    while camera.IsGrabbing():
        # Retrieve grab result (timeout set to 5000ms)
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            # Convert the buffer to a usable NumPy array for OpenCV
            converted_frame = converter.Convert(grab_result)
            img = converted_frame.GetArray()

            # Write frame to video file
            video_writer.write(img)

            # Display the continuous live stream
            cv2.imshow('Basler PoE Camera Stream', img)

            # Break the loop if 'q' is pressed
            if cv2.getStructuringKey(1) & 0xFF == ord('q'):
                break
        
        grab_result.Release()

except Exception as e:
    print(f"An error occurred during streaming: {e}")

finally:
    # 6. Clean up resources properly
    camera.StopGrabbing()
    camera.Close()
    video_writer.release()
    cv2.destroyAllWindows()
    print("Recording stopped. File saved successfully.")
