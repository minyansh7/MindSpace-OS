"""
Mobile detection helper for MindSpace OS.

Usage:

    from mobile import is_mobile

    if is_mobile():
        # mobile-optimized render path
        ...
    else:
        # desktop path — UNCHANGED
        ...

Detection is via User-Agent sniffing through Streamlit's `st.context.headers`
API (available since Streamlit 1.37). User-Agent reading runs server-side so
there's no page flicker and no dependency on third-party JS components.

Fallback: if `st.context` is unavailable or the header is missing,
`is_mobile()` returns False (assume desktop), which is the safer default
because the desktop branch is the canonical rendering.

Design principle: this helper exists so every page can gate mobile-specific
behavior like this:

    if not is_mobile():
        st.plotly_chart(fig, use_container_width=True, config=config)  # desktop
    else:
        mobile_fig = build_mobile_variant(fig)
        st.plotly_chart(mobile_fig, use_container_width=True, config=mobile_config)

The `if not is_mobile()` ordering keeps the desktop branch first/canonical so
diffs stay minimal and it's obvious at a glance that desktop behavior is
untouched.
"""
from __future__ import annotations

import re

import streamlit as st

# Broad-but-conservative UA match. Covers iOS (iPhone / iPad), Android
# phones, and anything self-identifying with "Mobi". Tablets on Android
# typically include "Mobile" so they match; iPads self-identify as
# "iPad" (older) or "Macintosh" on iPadOS 13+ (not reliably detectable
# via UA — those will fall through to the desktop branch, which is the
# acceptable default).
_MOBILE_UA_RE = re.compile(r"Mobi|Android|iPhone|iPad", re.IGNORECASE)


def is_mobile() -> bool:
    """Return True if the current request appears to come from a mobile device.

    Safe to call on every rerun. Never raises. If Streamlit's context API is
    unavailable or the User-Agent header is missing, returns False (assume
    desktop, which is the canonical rendering path).
    """
    try:
        ua = st.context.headers.get("User-Agent", "") or ""
    except Exception:
        # st.context was added in Streamlit 1.37. On older versions or
        # during unit-test imports it may not exist — treat as desktop.
        return False
    return bool(_MOBILE_UA_RE.search(ua))
