import cv2
import numpy as np

def extract_noise(image: np.ndarray) -> float:
    """
    Compute noise level of BGR image in range [0, 1.0].
    Estimates noise standard deviation by differencing with Gaussian blur.
    """
    if image is None:
        return 0.5
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.5)
    
    diff = cv2.absdiff(gray, blurred)
    std_diff = float(np.std(diff))
    
    # Normalize: typical noise standard deviation is [0, 15]
    return np.clip(std_diff / 15.0, 0.0, 1.0)
