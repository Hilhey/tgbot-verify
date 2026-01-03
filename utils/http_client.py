"""Helper untuk membuat HTTP client dengan dukungan proxy."""
from __future__ import annotations

from typing import Optional
import httpx


def create_client(timeout: float = 30.0, proxy: Optional[str] = None) -> httpx.Client:
    if not proxy:
        return httpx.Client(timeout=timeout)
    try:
        return httpx.Client(timeout=timeout, proxies=proxy)
    except TypeError:
        try:
            return httpx.Client(timeout=timeout, proxy=proxy)
        except TypeError:
            return httpx.Client(timeout=timeout)


def create_async_client(timeout: float = 30.0, proxy: Optional[str] = None) -> httpx.AsyncClient:
    if not proxy:
        return httpx.AsyncClient(timeout=timeout)
    try:
        return httpx.AsyncClient(timeout=timeout, proxies=proxy)
    except TypeError:
        try:
            return httpx.AsyncClient(timeout=timeout, proxy=proxy)
        except TypeError:
            return httpx.AsyncClient(timeout=timeout)
