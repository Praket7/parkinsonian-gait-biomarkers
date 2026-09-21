"""Use the existing official-only CARE-PD matched route without a new conversion."""
from __future__ import annotations
from src.carepd_analysis import analyze_carepd_directory


def run(directory, *, h36m_root=None, min_participants=8):
    return analyze_carepd_directory(directory, h36m_root=h36m_root, min_participants=min_participants)
