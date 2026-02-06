"""HTTP client for upstream API proxy."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx

from gateway.proxy.canary import CanaryRouter, load_canary_config


class ProxyClient:
    """Shared httpx client for upstream API requests."""

    def __init__(
        self,
        upstream_base_url: str,
        upstream_canary_base_url: str | None = None,
        canary_config_path: str | None = None,
        debug_mode: bool | None = None,
        connect_timeout: float = 10.0,
        read_timeout: float = 30.0,
        write_timeout: float = 10.0,
        pool_timeout: float = 5.0,
    ):
        """
        Initialize proxy client.

        Args:
            upstream_base_url: Base URL for legacy/current upstream API
            upstream_canary_base_url: Optional base URL for canary upstream API
            canary_config_path: Path to canary config file (defaults to CANARY_CONFIG_PATH env var)
            debug_mode: Whether debug headers are enabled (defaults to GATEWAY_DEBUG_PROXY env var)
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            write_timeout: Write timeout in seconds
            pool_timeout: Pool timeout in seconds
        """
        # Validate URLs with httpx.URL to fail fast with clear errors
        try:
            httpx.URL(upstream_base_url)
        except Exception as e:
            raise ValueError(f"Invalid UPSTREAM_BASE_URL: {upstream_base_url}") from e
        
        if upstream_canary_base_url:
            try:
                httpx.URL(upstream_canary_base_url)
            except Exception as e:
                raise ValueError(f"Invalid UPSTREAM_CANARY_BASE_URL: {upstream_canary_base_url}") from e

        self.upstream_base_url = upstream_base_url.rstrip("/")
        self.upstream_canary_base_url = (
            upstream_canary_base_url.rstrip("/") if upstream_canary_base_url else None
        )

        # Load canary config once at initialization
        if canary_config_path is None:
            canary_config_path = os.getenv("CANARY_CONFIG_PATH", "canary_config.json")
        self.canary_router = load_canary_config(canary_config_path)

        # Compute debug mode once at initialization
        if debug_mode is None:
            debug_mode = os.getenv("GATEWAY_DEBUG_PROXY", "").lower() in {"1", "true", "yes"}
        self.debug_mode = debug_mode

        # Create httpx client with explicit timeouts and no retries
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=write_timeout,
                pool=pool_timeout,
            ),
            follow_redirects=False,  # Don't follow redirects, pass them through
        )

    async def close(self) -> None:
        """Close the httpx client."""
        await self.client.aclose()

    def get_upstream_url(self, path: str, use_canary: bool = False) -> str:
        """
        Get full upstream URL for a path.

        Args:
            path: Request path (should start with /)
            use_canary: Whether to use canary upstream

        Returns:
            Full URL
        """
        base = self.upstream_canary_base_url if use_canary else self.upstream_base_url
        if not path.startswith("/"):
            path = "/" + path
        return f"{base}{path}"


# Global proxy client instance
_proxy_client: ProxyClient | None = None


def get_proxy_client() -> ProxyClient:
    """Get the global proxy client instance."""
    if _proxy_client is None:
        raise RuntimeError("Proxy client not initialized. Call init_proxy_client() first.")
    return _proxy_client


def init_proxy_client() -> ProxyClient:
    """
    Initialize the global proxy client from environment variables.

    Returns:
        Initialized ProxyClient instance
    """
    global _proxy_client

    upstream_base_url = os.getenv("UPSTREAM_BASE_URL")
    if not upstream_base_url:
        raise ValueError("UPSTREAM_BASE_URL environment variable is required")

    upstream_canary_base_url = os.getenv("UPSTREAM_CANARY_BASE_URL")
    canary_config_path = os.getenv("CANARY_CONFIG_PATH", "canary_config.json")
    debug_mode = os.getenv("GATEWAY_DEBUG_PROXY", "").lower() in {"1", "true", "yes"}

    _proxy_client = ProxyClient(
        upstream_base_url=upstream_base_url,
        upstream_canary_base_url=upstream_canary_base_url,
        canary_config_path=canary_config_path,
        debug_mode=debug_mode,
    )

    return _proxy_client


@asynccontextmanager
async def proxy_client_lifespan() -> AsyncGenerator[ProxyClient, None]:
    """
    Lifespan context manager for proxy client.

    Usage:
        app = FastAPI(lifespan=proxy_client_lifespan)
    """
    client = init_proxy_client()
    try:
        yield client
    finally:
        await client.close()
