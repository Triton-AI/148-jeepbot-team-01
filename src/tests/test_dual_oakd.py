import cv2
import depthai as dai

def create_pipeline():
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)

    xout_rgb.setStreamName("rgb")
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.preview.link(xout_rgb.input)

    return pipeline

def main():
    devices = dai.Device.getAllAvailableDevices()

    if len(devices) < 2:
        print("Less than two OAK-D devices detected.")
        return

    pipeline1 = create_pipeline()
    pipeline2 = create_pipeline()

    with dai.Device(pipeline1, devices[0]) as dev1, dai.Device(pipeline2, devices[1]) as dev2:
        q1 = dev1.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        q2 = dev2.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            frame1 = q1.get().getCvFrame()
            frame2 = q2.get().getCvFrame()

            cv2.imshow("OAK-D 1", frame1)
            cv2.imshow("OAK-D 2", frame2)

            if cv2.waitKey(1) == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
