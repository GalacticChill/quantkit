"""Tiny HTTP helper with an on-disk cache.

Keeps the loaders keyless and polite: a downloaded URL is cached under
``~/.cache/quantkit`` and reused until it is older than ``ttl`` seconds.
Cache failures are swallowed — a caching problem must never break a fetch.
"""
from __future__ import annotations

import hashlib
import os
import time
import urllib.request

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "quantkit")
USER_AGENT = "quantkit/0.1 (+https://github.com/GalacticChill/quantkit)"


def _cache_path(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    return os.path.join(CACHE_DIR, digest)


def fetch(url: str, *, cache: bool = True, ttl: int = 86_400, timeout: int = 60) -> bytes:
    """Return the bytes at ``url``, using a disk cache when ``cache`` is True."""
    if cache:
        path = _cache_path(url)
        try:
            if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < ttl:
                with open(path, "rb") as fh:
                    return fh.read()
        except OSError:
            pass

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()

    if cache:
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(_cache_path(url), "wb") as fh:
                fh.write(data)
        except OSError:
            pass
    return data
