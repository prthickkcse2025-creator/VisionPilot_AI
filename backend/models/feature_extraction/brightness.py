import cv2
import numpy as np

def extract_brightness(image: np.ndarray) -> float:
    """
    Compute average brightness of the BGR image in range [0, 1.0].
    """
    if image is None:
        return 0.5
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray))
    return np.clip(mean_val / 255.0, 0.0, 1.0)
