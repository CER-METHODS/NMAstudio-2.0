"""
SKT (Knowledge Translation) Local Storage

Separate storage components specific to the SKT/Knowledge Translation page.
These are kept separate from the main STORAGE to avoid bloating the core schema.

Usage:
    from assets.skt_storage import SKT_STORAGE, SKT_STORAGE_SCHEMA
"""

from dash import dcc

# Storage type - same as main storage for consistency
SESSION_TYPE = "local"

# ============================================================================
# SKT STORAGE SCHEMA
# ============================================================================
#
# treatment_fullnames_SKT:
#   Dict mapping treatment abbreviations to full names
#   Example: {"ADA": "Adalimumab", "PBO": "Placebo", ...}
#
# ============================================================================

SKT_STORAGE_SCHEMA = {
    "treatment_fullnames_SKT": "dict",  # Treatment abbreviation -> full name mapping
}

SKT_EMPTY_STORAGE = {
    "treatment_fullnames_SKT": {},
}

SKT_STORAGE_KEYS = list(SKT_STORAGE_SCHEMA.keys())


def skt_storage_components():
    """
    Returns the dcc.Store components for SKT-specific storage.
    Add these to your app layout alongside the main STORAGE components.
    """
    return [
        dcc.Store(id="treatment_fullnames_SKT", data=None, storage_type=SESSION_TYPE),
    ]


# For convenience - pre-instantiated storage components
SKT_STORAGE = skt_storage_components()
