"""Optional ecosystem integrations."""

from .huggingface import is_available as hf_available
from .llama_cpp import is_available as llama_cpp_available

__all__ = ["hf_available", "llama_cpp_available"]
