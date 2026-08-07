import cv2
import numpy as np

def extract_contrast(image: np.ndarray) -> float:
    """
    Compute contrast of the BGR image in range [0, 1.0].
    Uses the standard deviation of grayscale luminance.
    """
    if image is None:
        return 0.5
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    std_val = float(np.std(gray))
    # Standard deviation maximum is ~127.5. Normalize by dividing by 75.0 and clipping
    return np.clip(std_val / 75.0, 0.0, 1.0)
