import cv2
import numpy as np

def extract_dynamic_range(image: np.ndarray) -> float:
    """
    Compute normalized dynamic range of BGR image in range [0, 1.0].
    Estimates spread between the 99th and 1st percentiles of luminance.
    """
    if image is None:
        return 0.5
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    p99 = np.percentile(gray, 99)
    p01 = np.percentile(gray, 1)
    
    diff = float(p99 - p01)
    return np.clip(diff / 255.0, 0.0, 1.0)
