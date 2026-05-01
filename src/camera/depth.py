import cv2
import depthai as dai
import numpy as np

def main():
    pipeline = dai.Pipeline()

    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_right = pipeline.create(dai.node.MonoCamera)
    stereo = pipeline.create(dai.node.StereoDepth)
    xout_depth = pipeline.create(dai.node.XLinkOut)

    xout_depth.setStreamName("depth")

    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)

    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)

    mono_left.out.link(stereo.left)
    mono_right.out.link(stereo.right)
    stereo.depth.link(xout_depth.input)

    with dai.Device(pipeline) as device:
        q_depth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        while True:
            in_depth = q_depth.get()
            depth_frame = in_depth.getFrame()

            depth_vis = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
            depth_vis = np.uint8(depth_vis)
            depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)

            cv2.imshow("Depth Map", depth_vis)

            if cv2.waitKey(1) == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
