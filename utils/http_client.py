"""Helper untuk membuat HTTP client dengan dukungan proxy."""
from __future__ import annotations

from typing import Optional
import httpx


def _normalize_proxy(proxy: Optional[str]) -> Optional[str]:
    if not proxy:
        return None
    value = proxy.strip()
    if "://" not in value:
        value = f"http://{value}"
    return value


def create_client(timeout: float = 30.0, proxy: Optional[str] = None) -> httpx.Client:
    normalized_proxy = _normalize_proxy(proxy)
    if not normalized_proxy:
        return httpx.Client(timeout=timeout)
    try:
        return httpx.Client(timeout=timeout, proxies=normalized_proxy)
    except TypeError:
        try:
            return httpx.Client(timeout=timeout, proxy=normalized_proxy)
        except TypeError:
            return httpx.Client(timeout=timeout)


def create_async_client(timeout: float = 30.0, proxy: Optional[str] = None) -> httpx.AsyncClient:
    normalized_proxy = _normalize_proxy(proxy)
    if not normalized_proxy:
        return httpx.AsyncClient(timeout=timeout)
    try:
        return httpx.AsyncClient(timeout=timeout, proxies=normalized_proxy)
    except TypeError:
        try:
            return httpx.AsyncClient(timeout=timeout, proxy=normalized_proxy)
        except TypeError:
            return httpx.AsyncClient(timeout=timeout)
