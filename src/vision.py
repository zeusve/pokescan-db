"""Vision module: deterministic image hashing for visual similarity search."""

import cv2
import imagehash
import numpy as np
from PIL import Image


class ImageHasher:
    """Generates 512-dimension vectors and perceptual hashes from card images.

    Dimensions are defined as class constants (P2 — zero hardcoding).
    Processing is purely functional: same input → same output (P9 — idempotency).
    Interpolation is fixed to cv2.INTER_AREA for determinism (P6).
    """

    WIDTH = 32
    HEIGHT = 16
    VECTOR_DIM = WIDTH * HEIGHT  # 512

    INTERPOLATION = cv2.INTER_AREA
    COLOR_SPACE = cv2.COLOR_BGR2GRAY

    @classmethod
    def to_vector(cls, image_bytes: bytes) -> list[float]:
        """Convert raw image bytes to a normalized 512-dimension float vector.

        Pipeline:
            1. Decode bytes → BGR image (OpenCV default).
            2. Convert to grayscale (deterministic color space).
            3. Resize to WIDTH×HEIGHT using INTER_AREA (deterministic interpolation).
            4. Normalize pixel values to [0, 1].
            5. Flatten to 1-D list of floats.
        """
        buf = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image")

        gray = cv2.cvtColor(img, cls.COLOR_SPACE)
        resized = cv2.resize(gray, (cls.WIDTH, cls.HEIGHT), interpolation=cls.INTERPOLATION)
        normalized = resized.astype(np.float64) / 255.0
        return normalized.flatten().tolist()

    @classmethod
    def to_phash(cls, image_bytes: bytes) -> str:
        """Compute a 64-bit perceptual hash (hex string) from raw image bytes."""
        buf = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image")

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        return str(imagehash.phash(pil_image))
