import cv2
import numpy as np

def extract_perspective_skew(image: np.ndarray) -> float:
    """
    Compute perspective distortion or rotation skew score in range [0, 1.0].
    Estimates dominant angles using Hough line transform.
    """
    if image is None:
        return 0.0
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Run Canny edge detector
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Run HoughLinesP to detect linear segments
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
    
    if lines is None or len(lines) == 0:
        return 0.0
        
    angles = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            # Normalize angles to [-45, 45] degrees
            if angle > 45:
                angle -= 90
            elif angle < -45:
                angle += 90
            angles.append(abs(angle))
            
    median_angle = float(np.median(angles)) if angles else 0.0
    
    # Normalize: typical skews range [0, 15] degrees. Map to [0.0, 1.0]
    return np.clip(median_angle / 15.0, 0.0, 1.0)
