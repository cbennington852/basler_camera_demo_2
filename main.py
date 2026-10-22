from pypylon import pylon

# Create an InstantCamera object for the first camera device found
with pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice()) as camera:
    camera.Open()
    print(f"Connected to: {camera.DeviceInfo.ModelName}")

    # Grab a single frame with a timeout of 5000 milliseconds
    grab_result = camera.GrabOne(5000)

    if grab_result.GrabSucceeded():
        # Display the image using Pylon's internal viewer
        pylon.DisplayImage(1, grab_result)
    else:
        print(f"Error: {grab_result.ErrorCode} - {grab_result.ErrorDescription}")
        
    grab_result.Release()
