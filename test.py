import cv2
from pypylon import pylon

def main():
    # 1. Create an InstantCamera instance for the first found camera
    # This abstract factory handles the camera lifestyle and underlying GigE/USB transport layers.
    try:
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        camera.Open()
        print(f"Connected to device: {camera.GetDeviceInfo().GetModelName()}")
    except Exception as e:
        print(f"Error opening camera: {e}")
        return

    # 2. Configure camera parameters (Optional)
    # Note: For GigE cameras, settings like Packet Size can also be tuned here.
    camera.Width.SetValue(camera.Width.Max)
    camera.Height.SetValue(camera.Height.Max)

    # 3. Start grabbing images
    # Strategy_LatestImageOnly ensures we always grab the most recent frame in the buffer.
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    
    # Create an OpenCV converter to format the pypylon image structure to BGR/RGB
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    print("Press 'q' in the video window to exit.")

    while camera.IsGrabbing():
        # Retrieve the grab result from the camera with a 5000ms timeout
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Convert the buffer to a numpy array for OpenCV compatibility
            image = converter.Convert(grabResult)
            img = image.GetArray()

            # Display the stream using OpenCV
            cv2.imshow('Basler GigE Live Stream', img)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Must release the grab result back to the driver's buffer loop
        grabResult.Release()

    # 4. Clean up
    camera.StopGrabbing()
    camera.Close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
