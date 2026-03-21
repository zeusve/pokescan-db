"""Project-wide constants (P2 — zero hardcoding).

Lightweight module with no heavy dependencies so it can be safely
imported by models.py, Alembic migrations, and any other context
without pulling in OpenCV / NumPy / PIL.
"""

# Image hash vector dimensions: 32 (width) × 16 (height) = 512
VECTOR_DIM = 512
