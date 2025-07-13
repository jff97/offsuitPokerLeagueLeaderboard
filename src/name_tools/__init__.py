"""
Name tools package for poker tournament data.
Contains utilities for name clash detection and name resolution.
"""

from .name_clash_detector import detect_name_clashes
from .determine_name_ambiguities import determine_name_actions, write_results_to_txt, normalize, split_name

__all__ = [
    'detect_name_clashes',
]
