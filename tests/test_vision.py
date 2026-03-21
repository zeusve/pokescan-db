"""Tests for src.vision — ImageHasher vector generation and perceptual hashing."""

import numpy as np
import pytest

from src.vision import ImageHasher


def _make_image(width: int, height: int, color: tuple[int, int, int]) -> bytes:
    """Generate a synthetic BGR image encoded as PNG bytes."""
    import cv2

    img = np.full((height, width, 3), color, dtype=np.uint8)
    _, buf = cv2.imencode(".png", img)
    return buf.tobytes()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def red_image() -> bytes:
    return _make_image(200, 300, (0, 0, 255))


@pytest.fixture
def blue_image() -> bytes:
    return _make_image(200, 300, (255, 0, 0))


@pytest.fixture
def black_image() -> bytes:
    return _make_image(100, 100, (0, 0, 0))


@pytest.fixture
def white_image() -> bytes:
    return _make_image(100, 100, (255, 255, 255))


@pytest.fixture
def tiny_image() -> bytes:
    """1x1 pixel edge-case image."""
    return _make_image(1, 1, (128, 64, 32))


@pytest.fixture
def large_image() -> bytes:
    """4K-ish image for performance sanity check."""
    return _make_image(3840, 2160, (42, 170, 200))


# ---------------------------------------------------------------------------
# Tests: to_vector
# ---------------------------------------------------------------------------

class TestToVector:
    def test_vector_dimensions(self, red_image: bytes) -> None:
        vec = ImageHasher.to_vector(red_image)
        assert len(vec) == ImageHasher.VECTOR_DIM

    def test_idempotency(self, red_image: bytes) -> None:
        vec1 = ImageHasher.to_vector(red_image)
        vec2 = ImageHasher.to_vector(red_image)
        assert vec1 == vec2

    def test_different_images_produce_different_vectors(
        self, red_image: bytes, blue_image: bytes
    ) -> None:
        vec_red = ImageHasher.to_vector(red_image)
        vec_blue = ImageHasher.to_vector(blue_image)
        assert vec_red != vec_blue

    def test_values_normalized_zero_to_one(self, red_image: bytes) -> None:
        vec = ImageHasher.to_vector(red_image)
        assert all(0.0 <= v <= 1.0 for v in vec)

    def test_black_image_all_zeros(self, black_image: bytes) -> None:
        vec = ImageHasher.to_vector(black_image)
        assert all(v == 0.0 for v in vec)

    def test_white_image_all_ones(self, white_image: bytes) -> None:
        vec = ImageHasher.to_vector(white_image)
        assert all(v == 1.0 for v in vec)

    def test_tiny_image(self, tiny_image: bytes) -> None:
        vec = ImageHasher.to_vector(tiny_image)
        assert len(vec) == ImageHasher.VECTOR_DIM

    def test_large_image(self, large_image: bytes) -> None:
        vec = ImageHasher.to_vector(large_image)
        assert len(vec) == ImageHasher.VECTOR_DIM

    def test_invalid_bytes_raises(self) -> None:
        with pytest.raises(ValueError, match="Could not decode image"):
            ImageHasher.to_vector(b"not-an-image")

    def test_output_type_is_list_of_floats(self, red_image: bytes) -> None:
        vec = ImageHasher.to_vector(red_image)
        assert isinstance(vec, list)
        assert all(isinstance(v, float) for v in vec)


# ---------------------------------------------------------------------------
# Tests: to_phash
# ---------------------------------------------------------------------------

class TestToPhash:
    def test_phash_format(self, red_image: bytes) -> None:
        h = ImageHasher.to_phash(red_image)
        assert isinstance(h, str)
        assert len(h) == 16  # 64-bit hash -> 16 hex chars
        int(h, 16)  # must be valid hex

    def test_phash_idempotency(self, red_image: bytes) -> None:
        h1 = ImageHasher.to_phash(red_image)
        h2 = ImageHasher.to_phash(red_image)
        assert h1 == h2

    def test_phash_different_images(self) -> None:
        """Use patterned images — solid colors collapse to the same phash."""
        import cv2

        # Gradient image
        grad = np.zeros((100, 100, 3), dtype=np.uint8)
        grad[:, :, 0] = np.tile(np.arange(100, dtype=np.uint8), (100, 1))
        _, buf_grad = cv2.imencode(".png", grad)

        # Checkerboard image
        checker = np.zeros((100, 100, 3), dtype=np.uint8)
        checker[::2, ::2] = 255
        checker[1::2, 1::2] = 255
        _, buf_checker = cv2.imencode(".png", checker)

        h_grad = ImageHasher.to_phash(buf_grad.tobytes())
        h_checker = ImageHasher.to_phash(buf_checker.tobytes())
        assert h_grad != h_checker

    def test_phash_invalid_bytes_raises(self) -> None:
        with pytest.raises(ValueError, match="Could not decode image"):
            ImageHasher.to_phash(b"not-an-image")
