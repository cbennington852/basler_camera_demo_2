import cv2
from pypylon import pylon

def main():
    # 1. Define the specific IP address of your GigE camera
    CAMERA_IP = "10.1.1.57" 

    try:
        # 2. Filter device selection using a DeviceInfo object
        info = pylon.DeviceInfo()
        info.SetPropertyValue('IpAddress', CAMERA_IP) # <-- Pass the IP address here

        # 3. Create the camera using the targeted DeviceInfo
        tl_factory = pylon.TlFactory.GetInstance()
        camera = pylon.InstantCamera(tl_factory.CreateFirstDevice(info))
        
        camera.Open()
        print(f"Successfully connected to camera at {CAMERA_IP} ({camera.GetDeviceInfo().GetModelName()})")
    except Exception as e:
        print(f"Error opening camera at {CAMERA_IP}: {e}")
        return

    # From here, proceed with grabbing frames as usual...
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()
            cv2.imshow('Targeted GigE Stream', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        grabResult.Release()

    camera.StopGrabbing()
    camera.Close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
