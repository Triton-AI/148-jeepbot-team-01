import cv2
import depthai as dai

def main():
    pipeline = dai.Pipeline()

    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)

    xout_rgb.setStreamName("rgb")

    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.preview.link(xout_rgb.input)

    with dai.Device(pipeline) as device:
        q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            in_rgb = q_rgb.get()
            frame = in_rgb.getCvFrame()

            cv2.imshow("OAK-D RGB Feed", frame)

            if cv2.waitKey(1) == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
