import cv2

def extract_frame(video_path, output_path='samples/extracted_frame.jpg', time_sec=3):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}\nPlace a sample video at samples/sample_video.mp4 or use an image as input.")
    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
    success, frame = cap.read()
    if not success:
        # try reading first frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, frame = cap.read()
    if success:
        cv2.imwrite(output_path, frame)
        print(f"Frame saved to {output_path}")
    else:
        raise RuntimeError('Failed to extract frame from video.')
    cap.release()
