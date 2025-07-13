"""
Name tools package for poker tournament data.
Contains utilities for name clash detection and name resolution.
"""

from .name_clash_detector import detect_name_clashes
from .determine_name_ambiguities import write_results_to_txt

__all__ = [
    'detect_name_clashes',
]
