import cv2
import numpy as np

def extract_color_cast(image: np.ndarray) -> float:
    """
    Compute color cast of BGR image in range [0, 1.0].
    Measures deviation of chrominance (A and B channels in Lab color space) from neutral (128).
    """
    if image is None:
        return 0.5
        
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    _, a, b = cv2.split(lab)
    
    mean_a = float(np.mean(a))
    mean_b = float(np.mean(b))
    
    # Distance from neutral grey (128, 128)
    dist = np.sqrt((mean_a - 128) ** 2 + (mean_b - 128) ** 2)
    
    # Normalize: distance max in typical color casts is ~40
    return np.clip(dist / 40.0, 0.0, 1.0)
