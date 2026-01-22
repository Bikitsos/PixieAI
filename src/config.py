"""
PixieAI Configuration

Model and memory settings optimized for Apple Silicon with <16GB RAM.
"""

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# 4-bit quantized Gemma 2 9B - fits within ~6-7GB RAM
MODEL_ID = "mlx-community/gemma-2-9b-it-4bit"

# Memory budget breakdown:
# - Gemma 9B (4-bit): ~6-7 GB
# - macOS + GUI + Browser: ~9 GB
# - Total: < 16 GB ✅

# =============================================================================
# GENERATION SETTINGS
# =============================================================================

MAX_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9

# =============================================================================
# SEARCH SETTINGS
# =============================================================================

# Limit search results to save context tokens
MAX_SEARCH_RESULTS = 5

# =============================================================================
# HARDWARE SETTINGS
# =============================================================================

# MLX automatically uses Metal (GPU) backend on Apple Silicon
# CPU remains free for GUI and network tasks
USE_GPU = True  # MLX handles this automatically
