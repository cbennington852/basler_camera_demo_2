from pypylon import pylon

tl_factory = pylon.TlFactory.GetInstance()
tl = tl_factory.CreateTl('BaslerGigE')

cam_info = tl.CreateDeviceInfo()
cam_info.SetIpAddress('10.1.1.57') # Replace with your camera's IP

camera = pylon.InstantCamera(tl_factory.CreateDevice(cam_info))
camera.Open()
