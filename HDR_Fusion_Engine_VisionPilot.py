import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ==========================================
# 1. Color Space Conversions
# ==========================================

def rgb_to_ycbcr(img_rgb):
    """
    Convert RGB image (float, [0, 1]) to YCbCr channels.
    Y, Cb, Cr are returned in range [0, 1].
    BT.601 conversion formula is used.
    """
    r = img_rgb[:, :, 0]
    g = img_rgb[:, :, 1]
    b = img_rgb[:, :, 2]
    
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.168736 * r - 0.331264 * g + 0.5 * b + 0.5
    cr = 0.5 * r - 0.418688 * g - 0.081312 * b + 0.5
    
    return y, cb, cr

def ycbcr_to_rgb(y, cb, cr):
    """
    Convert YCbCr channels (float, [0, 1]) back to RGB image in [0, 1].
    """
    r = y + 1.402 * (cr - 0.5)
    g = y - 0.344136 * (cb - 0.5) - 0.714136 * (cr - 0.5)
    b = y + 1.772 * (cb - 0.5)
    
    rgb = np.stack([r, g, b], axis=-1)
    return np.clip(rgb, 0.0, 1.0)

# ==========================================
# 2. Edge-Aware Guided Luminosity Weight Maps (Phase 1 Improvement)
# ==========================================

def _smoothstep(edge0, edge1, x):
    """Hermite smoothstep: C1-continuous, zero-derivative at both edges."""
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-8), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def _quintic_smoothstep(edge0, edge1, x):
    """Quintic smoothstep: C2-continuous, zero 1st and 2nd derivatives at both edges."""
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-8), 0.0, 1.0)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

def _guided_filter(guide, src, radius=15, eps=1e-4):
    """
    Fast Guided Image Filter for edge-preserving weight map smoothing.
    Constrains weight transitions to physical structural edges in the guide image,
    eliminating spatial weight bleeding and patchy weight islands.
    """
    guide = guide.astype(np.float32)
    src = src.astype(np.float32)
    ksize = (2 * radius + 1, 2 * radius + 1)

    mean_g = cv2.boxFilter(guide, cv2.CV_32F, ksize)
    mean_p = cv2.boxFilter(src, cv2.CV_32F, ksize)
    mean_gp = cv2.boxFilter(guide * src, cv2.CV_32F, ksize)

    cov_gp = mean_gp - mean_g * mean_p
    mean_gg = cv2.boxFilter(guide * guide, cv2.CV_32F, ksize)
    var_g = mean_gg - mean_g * mean_g

    a = cov_gp / (var_g + eps)
    b = mean_p - a * mean_g

    mean_a = cv2.boxFilter(a, cv2.CV_32F, ksize)
    mean_b = cv2.boxFilter(b, cv2.CV_32F, ksize)

    q = mean_a * guide + mean_b
    return np.clip(q, 0.0, 1.0)

def _feather_mask(mask, image_shape):
    """
    Fallback Gaussian feathering.
    Sigma is ~1.5% of the shorter image dimension.
    """
    h, w = image_shape[:2]
    sigma = max(min(h, w) * 0.015, 2.0)
    ksize = int(sigma * 6) | 1  # 6-sigma kernel, forced odd
    return cv2.GaussianBlur(mask, (ksize, ksize), sigma)

def compute_luminance_weights(y_channels, use_edge_aware=True):
    """
    Compute edge-aware luminance (Y channel) blending weights.
    Eliminates patchy blending and spatial weight islands via guided structural filtering.
    """
    y_normal = y_channels[1]
    h, w = y_normal.shape

    if not use_edge_aware:
        # Legacy path for benchmarking & rollback comparison
        w_under = _smoothstep(0.88, 0.98, y_normal)
        w_over = 1.0 - _smoothstep(0.02, 0.12, y_normal)
        w_under = _feather_mask(w_under, y_normal.shape)
        w_over = _feather_mask(w_over, y_normal.shape)
        w_normal = np.clip(1.0 - w_under - w_over, 0.0, 1.0)
        return [w_under, w_normal, w_over]

    # Continuous C2 quintic smoothstep transitions
    w_under_raw = _quintic_smoothstep(0.82, 0.96, y_normal)
    w_over_raw = 1.0 - _quintic_smoothstep(0.04, 0.18, y_normal)

    # Well-exposedness gaussian weight for normal exposure
    sigma_exp = 0.25
    w_well_exposed = np.exp(-((y_normal - 0.5) ** 2) / (2.0 * sigma_exp ** 2))
    w_normal_raw = np.clip(w_well_exposed * (1.0 - w_under_raw) * (1.0 - w_over_raw), 0.001, 1.0)

    # Fast Guided Filtering aligned to structural edges of y_normal
    radius = max(int(min(h, w) * 0.015), 5)
    w_under_guided = _guided_filter(y_normal, w_under_raw, radius=radius, eps=1e-4)
    w_over_guided = _guided_filter(y_normal, w_over_raw, radius=radius, eps=1e-4)
    w_normal_guided = _guided_filter(y_normal, w_normal_raw, radius=radius, eps=1e-4)

    # Strict spatial weight sum normalization (sum to 1.0 per pixel)
    w_sum = w_under_guided + w_normal_guided + w_over_guided + 1e-8
    w_under = w_under_guided / w_sum
    w_normal = w_normal_guided / w_sum
    w_over = w_over_guided / w_sum

    return [w_under, w_normal, w_over]

def compute_chrominance_weights(y_channels, use_edge_aware=True):
    """
    Edge-aware weights for color channel (Cb, Cr) blending.
    Preserves normal exposure color fidelity while providing seamless transitions.
    """
    y_normal = y_channels[1]
    h, w = y_normal.shape

    if not use_edge_aware:
        # Legacy path for benchmarking & rollback comparison
        w_under = _smoothstep(0.93, 0.99, y_normal)
        w_over = 1.0 - _smoothstep(0.01, 0.07, y_normal)
        w_under = _feather_mask(w_under, y_normal.shape)
        w_over = _feather_mask(w_over, y_normal.shape)
        w_normal = np.clip(1.0 - w_under - w_over, 0.0, 1.0)
        return [w_under, w_normal, w_over]

    w_under_raw = _quintic_smoothstep(0.90, 0.98, y_normal)
    w_over_raw = 1.0 - _quintic_smoothstep(0.02, 0.10, y_normal)
    w_normal_raw = np.clip(1.0 - w_under_raw - w_over_raw, 0.001, 1.0)

    radius = max(int(min(h, w) * 0.015), 5)
    w_under_guided = _guided_filter(y_normal, w_under_raw, radius=radius, eps=1e-4)
    w_over_guided = _guided_filter(y_normal, w_over_raw, radius=radius, eps=1e-4)
    w_normal_guided = _guided_filter(y_normal, w_normal_raw, radius=radius, eps=1e-4)

    w_sum = w_under_guided + w_normal_guided + w_over_guided + 1e-8
    return [w_under_guided / w_sum, w_normal_guided / w_sum, w_over_guided / w_sum]

# ==========================================
# 3. Laplacian & Gaussian Pyramid Utilities
# ==========================================

def build_gaussian_pyramid(img, levels=6):
    pyramid = [img]
    for i in range(levels - 1):
        img = cv2.pyrDown(img)
        pyramid.append(img)
    return pyramid

def build_guided_weight_pyramids(weights, guide_images, levels=6, use_guided_weight_pyramid=True):
    """
    Constructs multi-scale weight map pyramids (Phase 3A Improvement).
    When use_guided_weight_pyramid=True, coarse levels (l >= 1) are guided by downsampled
    structural guide images (Y_normal) to prevent spatial weight edges from blurring across
    architectural boundaries (eliminates dark window mullion halos).
    """
    num_weights = len(weights)
    if not use_guided_weight_pyramid:
        return [build_gaussian_pyramid(w, levels) for w in weights]

    y_guide = guide_images[1] if len(guide_images) > 1 else guide_images[0]
    weight_pyramids = [[w] for w in weights]

    current_guide = y_guide
    current_weights = [w.copy() for w in weights]

    for l in range(1, levels):
        next_guide = cv2.pyrDown(current_guide)
        next_weights_raw = [cv2.pyrDown(w) for w in current_weights]

        h_l, w_l = next_guide.shape[:2]
        radius_l = max(int(min(h_l, w_l) * 0.015), 3)

        guided_w_list = []
        for w_raw in next_weights_raw:
            gw = _guided_filter(next_guide, w_raw, radius=radius_l, eps=1e-4)
            guided_w_list.append(gw)

        w_sum = sum(guided_w_list) + 1e-8
        norm_w_list = [gw / w_sum for gw in guided_w_list]

        for k in range(num_weights):
            weight_pyramids[k].append(norm_w_list[k])

        current_guide = next_guide
        current_weights = norm_w_list

    return weight_pyramids

def build_laplacian_pyramid(img, levels=6):
    gaussian_pyramid = build_gaussian_pyramid(img, levels)
    pyramid = []
    for i in range(levels - 1):
        h, w = gaussian_pyramid[i].shape[:2]
        upsampled = cv2.pyrUp(gaussian_pyramid[i+1], dstsize=(w, h))
        laplacian = gaussian_pyramid[i].astype(np.float64) - upsampled.astype(np.float64)
        pyramid.append(laplacian.astype(np.float32))
    pyramid.append(gaussian_pyramid[-1])
    return pyramid

def reconstruct_from_pyramid(laplacian_pyramid):
    levels = len(laplacian_pyramid)
    img = laplacian_pyramid[-1].astype(np.float64)
    for i in range(levels - 2, -1, -1):
        h, w = laplacian_pyramid[i].shape[:2]
        upsampled = cv2.pyrUp(img, dstsize=(w, h))
        img = upsampled + laplacian_pyramid[i].astype(np.float64)
    return img.astype(np.float32)

def compute_max_detail_texture_weights(image_pyramids, raw_images, level=0, gamma=1.5):
    """
    Computes per-pixel texture gradient energy weights for fine Laplacian detail bands (Phase 4A).
    E_k(x, y) = ||grad Y_k(x, y)||^2 masked to reject saturated highlights and clipped shadow noise.
    """
    texture_energies = []
    for k, img in enumerate(raw_images):
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            y_channel = 0.299 * img_rgb[:, :, 0] + 0.587 * img_rgb[:, :, 1] + 0.114 * img_rgb[:, :, 2]
        else:
            y_channel = img.astype(np.float32) / 255.0

        if level > 0:
            for _ in range(level):
                y_channel = cv2.pyrDown(y_channel)

        gx = cv2.Sobel(y_channel, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(y_channel, cv2.CV_32F, 0, 1, ksize=3)
        energy_raw = gx**2 + gy**2

        shadow_gate = _quintic_smoothstep(0.02, 0.08, y_channel)
        highlight_gate = 1.0 - _quintic_smoothstep(0.90, 0.96, y_channel)
        energy_masked = energy_raw * shadow_gate * highlight_gate

        texture_energies.append(energy_masked ** gamma)

    energy_sum = sum(texture_energies) + 1e-8
    norm_weights = [e / energy_sum for e in texture_energies]
    return norm_weights

def blend_pyramids(image_pyramids, weight_pyramids, decouple_fine_details=True, anchor_window_luminance=True, use_max_detail_texture_weights=False, raw_images=None):
    """
    Blends Laplacian pyramids across scales.
    - decouple_fine_details=True (Phase 2): Fine detail bands (l in {0, 1}) avoid spatial weight gradients.
    - anchor_window_luminance=True (Phase 3B): Coarse levels (l >= 2) anchor underexposed window background.
    - use_max_detail_texture_weights=False (Phase 4A Rollback): Restores exact Phase 3B scalar weighting path.
    """
    fused_pyramid = []
    levels = len(image_pyramids[0])
    num_images = len(image_pyramids)

    global_weights = None
    if decouple_fine_details and not use_max_detail_texture_weights:
        means = [np.mean(w_pyr[0]) for w_pyr in weight_pyramids]
        sum_means = sum(means) + 1e-8
        global_weights = [m / sum_means for m in means]

    for l in range(levels):
        fused_layer = np.zeros_like(image_pyramids[0][l], dtype=np.float64)

        if l in (0, 1):
            if use_max_detail_texture_weights and raw_images is not None:
                tex_weights = compute_max_detail_texture_weights(image_pyramids, raw_images, level=l, gamma=1.5)
                for img_pyr, tw in zip(image_pyramids, tex_weights):
                    w = tw
                    if len(fused_layer.shape) == 3 and len(w.shape) == 2:
                        w = np.expand_dims(w, axis=-1)
                    fused_layer += img_pyr[l].astype(np.float64) * w.astype(np.float64)
            elif decouple_fine_details:
                for img_pyr, g_w in zip(image_pyramids, global_weights):
                    fused_layer += img_pyr[l].astype(np.float64) * g_w
            else:
                for img_pyr, w_pyr in zip(image_pyramids, weight_pyramids):
                    w = w_pyr[l]
                    if len(fused_layer.shape) == 3 and len(w.shape) == 2:
                        w = np.expand_dims(w, axis=-1)
                    fused_layer += img_pyr[l].astype(np.float64) * w.astype(np.float64)
        else:
            if anchor_window_luminance and l >= 2 and num_images >= 3:
                w_under = weight_pyramids[0][l]
                y_normal_coarse = image_pyramids[1][l]

                ambient_mask = (y_normal_coarse >= 0.15) & (y_normal_coarse <= 0.85)
                mu_ambient = float(np.mean(y_normal_coarse[ambient_mask])) if np.any(ambient_mask) else 0.40
                target_min = mu_ambient * 1.25

                y_under_coarse = image_pyramids[0][l]
                y_under_anchored = np.maximum(y_under_coarse, target_min * w_under)

                for k, (img_pyr, w_pyr) in enumerate(zip(image_pyramids, weight_pyramids)):
                    w = w_pyr[l]
                    if len(fused_layer.shape) == 3 and len(w.shape) == 2:
                        w = np.expand_dims(w, axis=-1)
                    layer_data = y_under_anchored if k == 0 else img_pyr[l]
                    fused_layer += layer_data.astype(np.float64) * w.astype(np.float64)
            else:
                for img_pyr, w_pyr in zip(image_pyramids, weight_pyramids):
                    w = w_pyr[l]
                    if len(fused_layer.shape) == 3 and len(w.shape) == 2:
                        w = np.expand_dims(w, axis=-1)
                    fused_layer += img_pyr[l].astype(np.float64) * w.astype(np.float64)

        fused_pyramid.append(fused_layer.astype(np.float32))
    return fused_pyramid

def laplacian_blend(images, weights, levels=6, decouple_fine_details=True, use_guided_weight_pyramid=True, anchor_window_luminance=True, use_max_detail_texture_weights=False):
    """
    Blends a set of images using multi-scale Laplacian Pyramids.
    Phase 1: Edge-aware guided weight maps.
    Phase 2: Fine-detail decoupling (decouple_fine_details=True) for levels 0 & 1.
    Phase 3A: Guided coarse weight downsampling (use_guided_weight_pyramid=True) to eliminate window halos.
    Phase 3B: Window luminance anchoring (anchor_window_luminance=True) to eliminate pasted-on window appearance.
    Phase 4A: Max-detail texture weighting (use_max_detail_texture_weights=False by default for Phase 3B stability).
    """
    h, w = images[0].shape[:2]
    max_possible = int(np.log2(min(h, w))) - 2
    actual_levels = max(1, min(levels, max_possible))

    if actual_levels <= 1:
        fused = np.zeros_like(images[0], dtype=np.float64)
        for w_map, img in zip(weights, images):
            if len(fused.shape) == 3 and len(w_map.shape) == 2:
                w_map = np.expand_dims(w_map, axis=-1)
            fused += w_map * img
        return np.clip(fused, 0.0, 1.0).astype(np.float32)

    image_pyramids = [build_laplacian_pyramid(img, actual_levels) for img in images]

    # Phase 3A: Guided coarse weight downsampling
    weight_pyramids = build_guided_weight_pyramids(
        weights, images, levels=actual_levels, use_guided_weight_pyramid=use_guided_weight_pyramid
    )

    # Phase 2, 3B, 4A: Pyramid blending
    fused_pyramid = blend_pyramids(
        image_pyramids, weight_pyramids, decouple_fine_details=decouple_fine_details, anchor_window_luminance=anchor_window_luminance, use_max_detail_texture_weights=use_max_detail_texture_weights, raw_images=images
    )
    fused_img = reconstruct_from_pyramid(fused_pyramid)
    return np.clip(fused_img, 0.0, 1.0)

# ==========================================
# 4. PyTorch DeepFuse Model Definition
# ==========================================

class DeepFuseNet(nn.Module):
    def __init__(self):
        super(DeepFuseNet, self).__init__()
        
        # Shared encoding layers (using 3x3 kernels for fast, robust learning)
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        
        # Reconstruction layers (Decoder)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(32, 16, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(16, 1, kernel_size=3, padding=1)
        
    def forward(self, x1, x2, x3, target_y):
        # Feature extraction
        h1 = F.relu(self.conv2(F.relu(self.conv1(x1))))
        h2 = F.relu(self.conv2(F.relu(self.conv1(x2))))
        h3 = F.relu(self.conv2(F.relu(self.conv1(x3))))
        
        # Fusion layer: Element-wise maximum
        fused_features = torch.max(torch.max(h1, h2), h3)
        
        # Reconstruction
        out = F.relu(self.conv3(fused_features))
        out = F.relu(self.conv4(out))
        
        # Residual output scaled by 0.1 to guarantee stable initialization
        residual = torch.tanh(self.conv5(out)) * 0.1
        
        # Fused output is target Y channel plus small residual corrections
        fused_y = torch.clamp(target_y + residual, 0.0, 1.0)
        return fused_y

# ==========================================
# 5. Differentiable PyTorch SSIM Loss
# ==========================================

def create_gaussian_window(window_size, channel=1):
    def gaussian(window_size, sigma):
        gauss = torch.Tensor([np.exp(-(x - window_size // 2) ** 2 / float(2 * sigma ** 2)) for x in range(window_size)])
        return gauss / gauss.sum()
    _1D_window = gaussian(window_size, 1.5).unsqueeze(1)
    _2D_window = _1D_window.mm(_1D_window.t()).float().unsqueeze(0).unsqueeze(0)
    window = _2D_window.expand(channel, 1, window_size, window_size).contiguous()
    return window

def pytorch_ssim(img1, img2, window_size=11, size_average=True):
    device = img1.device
    channel = img1.size(1)
    window = create_gaussian_window(window_size, channel).to(device)
    
    mu1 = F.conv2d(img1, window, padding=window_size // 2, groups=channel)
    mu2 = F.conv2d(img2, window, padding=window_size // 2, groups=channel)
    
    mu1_sq = mu1.pow(2)
    mu2_sq = mu2.pow(2)
    mu1_mu2 = mu1 * mu2
    
    sigma1_sq = F.conv2d(img1 * img1, window, padding=window_size // 2, groups=channel) - mu1_sq
    sigma2_sq = F.conv2d(img2 * img2, window, padding=window_size // 2, groups=channel) - mu2_sq
    sigma12 = F.conv2d(img1 * img2, window, padding=window_size // 2, groups=channel) - mu1_mu2
    
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2
    
    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    
    if size_average:
        return ssim_map.mean()
    else:
        return ssim_map.mean(1).mean(1).mean(1)

# ==========================================
# 6. Multi-Exposure Fusion Algorithms
# ==========================================

def run_opencv_mertens(images):
    """
    Run baseline Mertens Exposure Fusion from OpenCV.
    Input images list of uint8 [H, W, 3] in BGR color space.
    """
    merge_mertens = cv2.createMergeMertens()
    fused_float = merge_mertens.process(images)
    fused_uint8 = np.clip(fused_float * 255.0, 0, 255).astype(np.uint8)
    return fused_uint8

def run_pytorch_weight_fusion(images):
    """
    Photorealistic exposure fusion emulating Photoshop luminosity masks.

    Architecture:
    - Luminance (Y): blended via Laplacian pyramids with narrow recovery zones.
    - Chrominance (Cb, Cr): blended with even narrower zones to prevent color shifts.
    - Normal exposure pixels are preserved exactly in all correctly-exposed regions.
    """
    # Convert images to range [0, 1] RGB
    images_rgb = [cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0 for img in images]
    
    # Convert to YCbCr
    y_channels = []
    cb_channels = []
    cr_channels = []
    
    for img in images_rgb:
        y, cb, cr = rgb_to_ycbcr(img)
        y_channels.append(y)
        cb_channels.append(cb)
        cr_channels.append(cr)

    # Luminance weights (narrow recovery zones, feathered)
    luma_weights = compute_luminance_weights(y_channels)

    # Fuse Y channel using Laplacian Pyramid Blending (6 levels)
    fused_y = laplacian_blend(y_channels, luma_weights, levels=6)

    # Chrominance weights (even narrower — preserve normal frame color almost everywhere)
    chroma_weights = compute_chrominance_weights(y_channels)

    # Fuse Cb/Cr channels with conservative chrominance weights
    fused_cb = np.zeros_like(cb_channels[0])
    fused_cr = np.zeros_like(cr_channels[0])
    for w, cb, cr in zip(chroma_weights, cb_channels, cr_channels):
        fused_cb += w * cb
        fused_cr += w * cr
    
    # Reconstruct RGB
    fused_rgb = ycbcr_to_rgb(fused_y, fused_cb, fused_cr)
    fused_bgr = cv2.cvtColor((fused_rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)
    
    return fused_bgr

def run_optimized_deep_fusion(images, epochs=50, lr=0.01, ssim_weight=0.8, progress_callback=None):
    """
    Photorealistic deep learning exposure fusion.

    Architecture:
    - Target Y computed from narrow luminosity-mask weights + Laplacian pyramid blending.
    - Residual CNN learns only micro-corrections on top of the already-perfect target.
    - Chrominance uses ultra-conservative weights to prevent any color leakage.
    """
    # 1. Prepare images in range [0, 1] RGB
    images_rgb = [cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0 for img in images]
    
    # Convert to YCbCr
    y_channels = []
    cb_channels = []
    cr_channels = []
    for img in images_rgb:
        y, cb, cr = rgb_to_ycbcr(img)
        y_channels.append(y)
        cb_channels.append(cb)
        cr_channels.append(cr)

    # Luminance weights for Y target generation
    luma_weights = compute_luminance_weights(y_channels)

    # Chrominance weights (ultra-conservative)
    chroma_weights = compute_chrominance_weights(y_channels)

    # Fuse chrominance with conservative weights
    fused_cb = np.zeros_like(cb_channels[0])
    fused_cr = np.zeros_like(cr_channels[0])
    for w, cb, cr in zip(chroma_weights, cb_channels, cr_channels):
        fused_cb += w * cb
        fused_cr += w * cr
    
    # Compute Target Y using Laplacian Pyramid Blending
    target_y = laplacian_blend(y_channels, luma_weights, levels=6)
        
    # 2. Downsample Y channels for both training and inference (max 768px)
    h, w = y_channels[0].shape
    max_dim = 768
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        nh, nw = int(h * scale), int(w * scale)
        y_train = [cv2.resize(y, (nw, nh), interpolation=cv2.INTER_AREA) for y in y_channels]
        target_y_train = cv2.resize(target_y, (nw, nh), interpolation=cv2.INTER_AREA)
    else:
        y_train = y_channels
        target_y_train = target_y
        
    # 3. Setup PyTorch variables
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Convert training data to PyTorch tensors
    t_y1 = torch.from_numpy(y_train[0]).unsqueeze(0).unsqueeze(0).to(device)
    t_y2 = torch.from_numpy(y_train[1]).unsqueeze(0).unsqueeze(0).to(device)
    t_y3 = torch.from_numpy(y_train[2]).unsqueeze(0).unsqueeze(0).to(device)
    t_target = torch.from_numpy(target_y_train).unsqueeze(0).unsqueeze(0).to(device)
    
    # Instantiate Model
    model = DeepFuseNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # 4. Optimization Loop (Unsupervised Training on Image Details)
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        # Feed target_y_train to residual network
        out = model(t_y1, t_y2, t_y3, t_target)
        
        # Loss: Weighted combination of SSIM (structure) and L1 (absolute levels)
        loss_ssim = 1.0 - pytorch_ssim(out, t_target)
        loss_l1 = F.l1_loss(out, t_target)
        loss = ssim_weight * loss_ssim + (1.0 - ssim_weight) * loss_l1
        
        loss.backward()
        optimizer.step()
        
        if progress_callback:
            progress_callback(epoch + 1, epochs, loss.item())
            
    # 5. Model Inference on Downsampled Images & Detail Injection
    model.eval()
    with torch.no_grad():
        fused_y_down_tensor = model(t_y1, t_y2, t_y3, t_target)
        fused_y_down = fused_y_down_tensor.squeeze().cpu().numpy()
        
    # Reconstruct final Y channel
    if scale != 1.0:
        # Upscale the CNN fused Y channel back to full resolution
        fused_y_up = cv2.resize(fused_y_down, (w, h), interpolation=cv2.INTER_CUBIC)
        
        # Extract high-frequency details from full-resolution target Y
        target_y_blur = cv2.GaussianBlur(target_y, (15, 15), 0)
        y_detail = target_y - target_y_blur
        
        # Inject details back into upscaled Y channel
        full_fused_y = np.clip(fused_y_up + y_detail, 0.0, 1.0)
    else:
        full_fused_y = fused_y_down
        
    # Reconstruct final RGB from fused Y, Cb, Cr
    fused_rgb = ycbcr_to_rgb(full_fused_y, fused_cb, fused_cr)
    fused_bgr = cv2.cvtColor((fused_rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)
    
    return fused_bgr

# ==========================================
# 7. Professional Refinement Pass
# ==========================================

def apply_refinement_pass(fused_bgr):
    """
    Professional retouching pipeline emulating a Lightroom + Photoshop workflow.
    7 sequential stages, each precisely calibrated to professional real estate standards:

    Stage 1 — Retinex Illumination Equalization:
        Decomposes Y = Reflectance × Illumination. Blends illumination 20%
        towards its global mean. Flattens ceiling light pools, preserves texture.

    Stage 2 — Clarity (Lightroom Clarity ~+30):
        Medium-frequency local contrast boost (σ = 2% of image dimension).
        Midtone-protected. Makes textures pop without halos.

    Stage 3 — Micro-Contrast Recovery:
        Small-frequency detail boost (σ = 0.5% of image). Noise-thresholded.

    Stage 4 — Fine Sharpening (Smart Sharpen):
        Ultra-fine USM (σ = 0.8px, amount = 0.25). Noise-thresholded.

    Stage 5 — Professional Tone Curve (Lightroom S-curve):
        Gentle polynomial S-curve: y' = y + 0.6·y·(1-y)·(y-0.5).
        Deepens shadows, adds midtone richness, soft highlight roll-off.
        Max shift ~3% (~7/255 levels). Black and white points preserved exactly.

    Stage 6 — White Balance + Warmth:
        Reduces blue/cyan cast 50% on cool Cb axis. Adds +0.003 Cr warm push
        in neutral areas only (Lightroom Temp +200K equivalent).

    Stage 7 — Vibrance (Lightroom Vibrance +12):
        Selective saturation: boosts muted colors more, protects saturated colors.

    This pass does NOT alter geometry, perspective, object positions, or the
    scene composition. It only enhances quality on the existing pixel data.
    """
    # Convert BGR to float32 RGB [0, 1]
    img_rgb = cv2.cvtColor(fused_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    y, cb, cr = rgb_to_ycbcr(img_rgb)

    h, w = y.shape

    # ── Stage 1: Retinex Illumination Equalization ──
    retinex_kernel = int(max(h, w) * 0.12) | 1  # ~12% of image, forced odd
    illumination = cv2.GaussianBlur(y, (retinex_kernel, retinex_kernel), 0)

    # Reflectance layer — clamp denominator to prevent noise amplification
    reflectance = y / np.maximum(illumination, 0.05)

    # Equalize illumination gently — 20% towards global mean
    mean_illum = np.mean(illumination)
    illumination_eq = 0.80 * illumination + 0.20 * mean_illum

    y_eq = np.clip(reflectance * illumination_eq, 0.0, 1.0)

    # ── Stage 2: Clarity Enhancement (medium-frequency local contrast) ──
    # Equivalent to Lightroom Clarity slider at ~+30
    clarity_sigma = max(min(h, w) * 0.02, 5.0)
    clarity_ksize = int(clarity_sigma * 6) | 1
    y_medium_blur = cv2.GaussianBlur(y_eq, (clarity_ksize, clarity_ksize), clarity_sigma)
    clarity_detail = y_eq - y_medium_blur

    # Protect near-black and near-white from clipping
    midtone_mask = _smoothstep(0.03, 0.08, y_eq) * (1.0 - _smoothstep(0.92, 0.97, y_eq))
    clarity_amount = 0.35
    y_clarity = np.clip(y_eq + clarity_amount * clarity_detail * midtone_mask, 0.0, 1.0)

    # ── Stage 3: Micro-Contrast Recovery (small-frequency detail) ──
    micro_sigma = max(min(h, w) * 0.005, 1.5)
    micro_ksize = int(micro_sigma * 6) | 1
    y_micro_blur = cv2.GaussianBlur(y_clarity, (micro_ksize, micro_ksize), micro_sigma)
    micro_detail = y_clarity - y_micro_blur

    # Noise-aware threshold: only boost genuine detail, not sensor noise
    detail_magnitude = np.abs(micro_detail)
    noise_threshold = 0.003  # ~0.75 / 255
    detail_mask = _smoothstep(noise_threshold, noise_threshold * 3.0, detail_magnitude)
    micro_amount = 0.30
    y_micro = np.clip(y_clarity + micro_amount * micro_detail * detail_mask, 0.0, 1.0)

    # ── Stage 4: Fine Detail Sharpening (unsharp mask) ──
    sharp_sigma = 0.8
    y_tiny_blur = cv2.GaussianBlur(y_micro, (3, 3), sharp_sigma)
    sharp_detail = y_micro - y_tiny_blur

    # Threshold to avoid sharpening noise
    sharp_magnitude = np.abs(sharp_detail)
    sharp_mask = _smoothstep(0.004, 0.012, sharp_magnitude)
    sharp_amount = 0.25
    y_refined = np.clip(y_micro + sharp_amount * sharp_detail * sharp_mask, 0.0, 1.0)

    # ── Stage 5: Professional Tone Curve (Lightroom S-curve) ──
    # Gentle S-curve centered at Y=0.5: deepens shadow contrast slightly,
    # adds midtone richness, maintains soft highlight roll-off.
    # Maximum luminance shift is ~3% (~7 levels) — invisible as an artifact,
    # but creates the "depth" and "pop" that separates amateur from professional.
    # Formula: y' = y + k * y * (1-y) * (y - 0.5)
    # This is zero at y=0 and y=1 (black/white preserved exactly).
    curve_strength = 0.6
    y_toned = np.clip(
        y_refined + curve_strength * y_refined * (1.0 - y_refined) * (y_refined - 0.5),
        0.0, 1.0
    )

    # ── Stage 6: White Balance + Warmth ──
    cb_corrected = np.copy(cb)
    cr_corrected = np.copy(cr)

    # Neutralize blue/cyan cast: reduce Cb deviation on the cool side by 50%
    blue_mask = cb > 0.5
    cb_corrected[blue_mask] = 0.5 + (cb[blue_mask] - 0.5) * 0.50

    # Subtle warm push in neutral areas only (equivalent to Lightroom Temp +200K)
    # Shifts Cr towards warm by 0.003 ONLY where both Cb and Cr are near 0.5.
    # Wood tones, colored furniture, and saturated objects are untouched.
    neutral_area = (np.abs(cb - 0.5) < 0.04) & (np.abs(cr - 0.5) < 0.04)
    cr_corrected[neutral_area] = cr[neutral_area] + 0.003

    # ── Stage 7: Vibrance (Lightroom Vibrance +12 equivalent) ──
    # Selective saturation: boosts muted/neutral colors more, protects
    # already-saturated colors from oversaturation. This is NOT flat saturation.
    sat = np.sqrt((cb_corrected - 0.5)**2 + (cr_corrected - 0.5)**2)
    max_sat = np.max(sat) + 1e-6
    vibrance_amount = 0.12
    boost = vibrance_amount * (1.0 - sat / max_sat)
    cb_final = np.clip(0.5 + (cb_corrected - 0.5) * (1.0 + boost), 0.0, 1.0)
    cr_final = np.clip(0.5 + (cr_corrected - 0.5) * (1.0 + boost), 0.0, 1.0)

    # Reconstruct RGB
    refined_rgb = ycbcr_to_rgb(y_toned, cb_final, cr_final)
    refined_bgr = cv2.cvtColor((refined_rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)

    return refined_bgr

# ==========================================
# 8. Quality Control Pass (200% Zoom Check)
# ==========================================

def apply_qc_pass(refined_bgr):
    """
    Final quality-control pass emulating a retoucher's 200% zoom inspection:

    1. Edge-preserving denoising (bilateral filter, 15% blend):
       Cleans residual sensor noise in smooth surfaces (ceiling, walls, floor)
       while preserving every hard edge. This is the equivalent of Lightroom's
       Luminance Noise Reduction at ~15.

    2. Final micro-sharpening (noise-thresholded unsharp mask):
       One last pass of ultra-gentle sharpening to ensure every edge is
       razor-crisp at print resolution. Amount is very low (0.15) to avoid
       any risk of ringing or halos.

    3. Residual color cast cleanup:
       One more pass of subtle Cb correction to catch any remaining cool tint
       that survived the first refinement.

    This pass does NOT alter geometry, composition, or object positions.
    """
    img_rgb = cv2.cvtColor(refined_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    y, cb, cr = rgb_to_ycbcr(img_rgb)

    # ── 1. Edge-Preserving Denoising (bilateral filter) ──
    y_u8 = (y * 255.0).astype(np.uint8)
    y_bilateral = cv2.bilateralFilter(y_u8, d=5, sigmaColor=8, sigmaSpace=5)
    y_smooth = y_bilateral.astype(np.float32) / 255.0

    # Blend: 85% original, 15% smoothed (only removes subtle noise)
    y_denoised = np.clip(0.85 * y + 0.15 * y_smooth, 0.0, 1.0)

    # ── 2. Final Micro-Sharpening ──
    y_blur = cv2.GaussianBlur(y_denoised, (3, 3), 0.7)
    sharp_detail = y_denoised - y_blur
    sharp_magnitude = np.abs(sharp_detail)
    sharp_mask = _smoothstep(0.005, 0.015, sharp_magnitude)
    y_final = np.clip(y_denoised + 0.15 * sharp_detail * sharp_mask, 0.0, 1.0)

    # ── 3. Residual Color Cast Cleanup ──
    cb_final = np.copy(cb)
    blue_residual = cb > 0.505  # catch anything still slightly cool
    cb_final[blue_residual] = 0.5 + (cb[blue_residual] - 0.5) * 0.85

    # Reconstruct RGB
    final_rgb = ycbcr_to_rgb(y_final, cb_final, cr)
    final_bgr = cv2.cvtColor((final_rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)

    return final_bgr

