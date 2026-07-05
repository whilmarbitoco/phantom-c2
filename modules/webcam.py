"""Webcam capture module."""
import os, time
def run(args):
    try:
        import cv2
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return {'status': 'error', 'error': 'camera unavailable', 'type': 'webcam'}
        ret, frame = cam.read()
        cam.release()
        if not ret:
            return {'status': 'error', 'error': 'frame capture failed', 'type': 'webcam'}
        path = '/tmp/webcam_' + str(int(time.time())) + '.jpg'
        cv2.imwrite(path, frame)
        return {'status': 'captured', 'filename': path, 'type': 'webcam', 'size': os.path.getsize(path)}
    except ImportError:
        return {'status': 'stub', 'filename': 'webcam.jpg', 'type': 'webcam', 'note': 'install opencv-python for capture'}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'type': 'webcam'}
