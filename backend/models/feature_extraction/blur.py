import cv2
import numpy as np

def extract_blur(image: np.ndarray) -> float:
    """
    Compute blur level of BGR image in range [0, 1.0].
    Uses the Variance of Laplacian (low variance indicates higher blur).
    Returns 1.0 for extremely blurry, 0.0 for extremely sharp.
    """
    if image is None:
        return 0.5
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # If image is very small, resizing to avoid Laplacian noise
    if gray.shape[0] < 50 or gray.shape[1] < 50:
        return 0.0
        
    var_val = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    
    # Normalize: map [0, 500+] to [1.0, 0.0]
    blur_score = 1.0 - (var_val / (var_val + 150.0))
    return np.clip(blur_score, 0.0, 1.0)
