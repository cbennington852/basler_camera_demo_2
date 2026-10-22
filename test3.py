import cv2
from pypylon import pylon

def main():
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
        return

    # Start live stream
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed

    print("Streaming... Press 'q' to quit.")
    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()
            cv2.imshow('GigE Stream with Custom Exposure', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        grabResult.Release()

    camera.StopGrabbing()
    camera.Close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
