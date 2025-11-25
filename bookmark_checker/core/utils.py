"""Utility functions for URL canonicalization and text normalization."""

import re
from urllib.parse import parse_qs, urlparse, urlunparse, urlencode

# Tracking parameters to remove (case-insensitive)
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "igshid",
    "yclid",
    "_hsenc",
    "_hsmi",
    "mkt_tok",
    "ref",
    "cmp",
    "spm",
    "ved",
    "si",
    "s",
    "trk",
    "scid",
    "ck_subscriber_id",
}


def canonicalize_url(url: str) -> str:
    """
    Canonicalize a URL by:
    - Lowercasing scheme and host
    - Stripping default ports (:80 for http, :443 for https)
    - Removing fragments (#...)
    - Removing trailing slash on non-root paths
    - Removing common tracking parameters
    - Preserving non-tracking parameters in stable order
    """
    if not url or not url.strip():
        return url

    try:
        parsed = urlparse(url.strip())
    except Exception:
        return url

    # Lowercase scheme and netloc (host)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Strip default ports
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # Remove fragment
    fragment = ""

    # Process query parameters
    query_params = parse_qs(parsed.query, keep_blank_values=False)
    filtered_params: dict[str, list[str]] = {}

    for key, values in query_params.items():
        key_lower = key.lower()
        if key_lower not in TRACKING_PARAMS:
            # Preserve original key case for non-tracking params
            filtered_params[key] = values

    # Rebuild query string with sorted keys for stability
    query = urlencode(sorted(filtered_params.items()), doseq=True) if filtered_params else ""

    # Remove trailing slash on non-root paths
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    # Reconstruct URL
    canonical = urlunparse((scheme, netloc, path, parsed.params, query, fragment))

    return canonical


def normalize_whitespace(s: str) -> str:
    """Normalize whitespace: collapse multiple spaces/tabs/newlines to single space, strip."""
    if not s:
        return ""
    return re.sub(r"\s+", " ", s.strip())


def domain_from_url(url: str) -> str:
    """Extract domain from URL, returning empty string if invalid."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        # Remove port if present
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        return netloc
    except Exception:
        return ""

