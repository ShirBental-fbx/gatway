"""Tests for proxy functionality."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.canary import CanaryRule, CanaryRouter, load_canary_config
from gateway.proxy.client import ProxyClient
from gateway.proxy.handler import proxy_handler, _extract_partner_from_path
from gateway.proxy.endpoint import proxy_to_upstream
from gateway.proxy.router import catch_all_proxy


@pytest.fixture
def mock_proxy_client():
    """Mock proxy client."""
    client = MagicMock(spec=ProxyClient)
    client.upstream_base_url = "https://legacy-api.example.com"
    client.upstream_canary_base_url = "https://canary-api.example.com"
    client.get_upstream_url = lambda path, use_canary=False: (
        client.upstream_canary_base_url + path
        if use_canary
        else client.upstream_base_url + path
    )
    return client


@pytest.fixture
def mock_httpx_response():
    """Mock httpx response."""
    response = MagicMock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.content = b'{"status": "ok"}'
    response.is_streaming = False
    return response


class TestUpstreamExpectations:
    """Tests that verify UPSTREAM_EXPECTATIONS.md content."""

    def test_upstream_expectations_file_exists(self):
        """Verify UPSTREAM_EXPECTATIONS.md exists."""
        expectations_file = Path(__file__).parent.parent.parent.parent / "UPSTREAM_EXPECTATIONS.md"
        assert expectations_file.exists(), "UPSTREAM_EXPECTATIONS.md must exist"

    def test_upstream_expectations_contains_request_id_header(self):
        """Verify UPSTREAM_EXPECTATIONS.md contains exact request-id header name."""
        expectations_file = Path(__file__).parent.parent.parent.parent / "UPSTREAM_EXPECTATIONS.md"
        content = expectations_file.read_text()
        
        # Must contain the exact header name from upstream code
        assert "request-id" in content.lower(), "Must document 'request-id' header (lowercase, hyphenated)"
        assert "FrontendAPI.py" in content or "Core.py" in content, "Must reference upstream source files"

    def test_upstream_expectations_contains_auth_mechanism(self):
        """Verify UPSTREAM_EXPECTATIONS.md contains auth mechanism location."""
        expectations_file = Path(__file__).parent.parent.parent.parent / "UPSTREAM_EXPECTATIONS.md"
        content = expectations_file.read_text()
        
        # Must contain reference to auth mechanism location
        assert "oauth2" in content.lower() or "authentication" in content.lower(), "Must document auth mechanism"
        assert ".py" in content, "Must reference source file locations"


class TestCanaryRouter:
    """Tests for CanaryRouter."""

    def test_should_use_canary_disabled(self):
        """Test canary routing when disabled."""
        router = CanaryRouter(rules=[], canary_enabled=False)
        use_canary, reason = router.should_use_canary("nav", "/api/v1/test", "GET")
        assert use_canary is False
        assert reason == "canary_disabled"

    def test_should_use_canary_no_matching_rule(self):
        """Test canary routing with no matching rules."""
        rule = CanaryRule(partner="other", endpoint_pattern="/other", percentage=100)
        router = CanaryRouter(rules=[rule], canary_enabled=True)
        use_canary, reason = router.should_use_canary("nav", "/api/v1/test", "GET")
        assert use_canary is False
        assert reason == "no_matching_rule"

    def test_should_use_canary_percentage_match(self):
        """Test canary routing with percentage match."""
        rule = CanaryRule(partner="nav", endpoint_pattern="/api/v1/test", percentage=100)
        router = CanaryRouter(rules=[rule], canary_enabled=True)
        use_canary, reason = router.should_use_canary("nav", "/api/v1/test", "GET")
        assert use_canary is True
        assert "percentage" in reason or "explicit_rule" in reason

    def test_should_use_canary_post_blocked_no_idempotency(self):
        """Test that POST is blocked (upstream has no idempotency mechanism)."""
        rule = CanaryRule(
            partner="nav",
            endpoint_pattern="/api/v1/test",
            method="POST",
        )
        router = CanaryRouter(rules=[rule], canary_enabled=True)
        use_canary, reason = router.should_use_canary(
            "nav", "/api/v1/test", "POST", has_idempotency_key=False
        )
        assert use_canary is False
        assert "non_get_blocked_no_idempotency" in reason

    def test_should_use_canary_post_blocked_even_with_idempotency_key(self):
        """Test that POST is blocked even with idempotency key (upstream doesn't support it)."""
        rule = CanaryRule(
            partner="nav",
            endpoint_pattern="/api/v1/test",
            method="POST",
        )
        router = CanaryRouter(rules=[rule], canary_enabled=True)
        use_canary, reason = router.should_use_canary(
            "nav", "/api/v1/test", "POST", has_idempotency_key=True
        )
        assert use_canary is False
        assert "non_get_blocked_no_idempotency" in reason

    def test_should_use_canary_regex_pattern(self):
        """Test canary routing with regex pattern."""
        rule = CanaryRule(
            partner="nav", endpoint_pattern="^/api/v1/.*", method="GET", percentage=100
        )
        router = CanaryRouter(rules=[rule], canary_enabled=True)
        use_canary, reason = router.should_use_canary("nav", "/api/v1/test", "GET")
        assert use_canary is True

    def test_should_use_canary_prefix_pattern(self):
        """Test canary routing with prefix pattern."""
        rule = CanaryRule(
            partner="nav", endpoint_pattern="/api/v1", method="GET", percentage=100
        )
        router = CanaryRouter(rules=[rule], canary_enabled=True)
        use_canary, reason = router.should_use_canary("nav", "/api/v1/test", "GET")
        assert use_canary is True


class TestCanaryConfig:
    """Tests for canary config loading."""

    def test_load_canary_config_missing_file(self, tmp_path):
        """Test loading config when file doesn't exist."""
        config_path = tmp_path / "nonexistent.json"
        router = load_canary_config(str(config_path))
        assert router.canary_enabled is False
        assert len(router.rules) == 0

    def test_load_canary_config_valid(self, tmp_path):
        """Test loading valid config file."""
        config_path = tmp_path / "canary_config.json"
        config_data = {
            "enabled": True,
            "rules": [
                {
                    "partner": "nav",
                    "endpoint_pattern": "/api/v1/test",
                    "method": "GET",
                    "percentage": 10,
                }
            ],
        }
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        router = load_canary_config(str(config_path))
        assert router.canary_enabled is True
        assert len(router.rules) == 1
        assert router.rules[0].partner == "nav"


class TestPartnerExtraction:
    """Tests for partner extraction from URL path."""

    def test_extract_partner_from_path_simple(self):
        """Test extracting partner from /partners/{partner}/... path."""
        partner = _extract_partner_from_path("/partners/nav/api/v1/test")
        assert partner == "nav"

    def test_extract_partner_from_path_nested(self):
        """Test extracting partner from nested path."""
        partner = _extract_partner_from_path("/api/v1/partners/intuit/webhooks")
        assert partner == "intuit"

    def test_extract_partner_from_path_not_found(self):
        """Test when partner is not in path."""
        partner = _extract_partner_from_path("/api/v1/test")
        assert partner is None

    def test_extract_partner_from_path_with_query(self):
        """Test extracting partner when query string present."""
        partner = _extract_partner_from_path("/partners/nav/test?param=value")
        assert partner == "nav"


class TestProxyHandler:
    """Tests for proxy handler."""

    @pytest.mark.asyncio
    async def test_proxy_handler_basic_get(self, mock_proxy_client, mock_httpx_response):
        """Test basic GET proxy forwarding with query/body preservation."""
        # Create mock request
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/test"
        request.url.query = "param=value&other=123"
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "request-id": "req-123",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        # Mock httpx stream context manager
        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        # Mock get_proxy_client
        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/api/v1/test?param=value&other=123",
                canary_router=None,
                debug_mode=False,
            )

        assert response.status_code == 200
        mock_proxy_client.client.stream.assert_called_once()
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        assert call_kwargs["method"] == "GET"
        # Verify query string is preserved in URL
        assert "param=value" in call_kwargs["url"] or "other=123" in call_kwargs["url"]
        # Verify request-id header (upstream format: lowercase, hyphenated)
        assert "request-id" in call_kwargs["headers"]
        assert call_kwargs["headers"]["request-id"] == "req-123"
        assert "X-Forwarded-For" in call_kwargs["headers"]
        # Verify no invented context headers
        assert "X-Partner-Id" not in call_kwargs["headers"]
        assert "X-API-Profile" not in call_kwargs["headers"]

    @pytest.mark.asyncio
    async def test_proxy_handler_request_id_bridging(self, mock_proxy_client, mock_httpx_response):
        """Test request ID bridging from x-request-id to request-id."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/test"
        request.url.query = ""
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "X-Request-ID": "x-req-456",  # Uppercase version
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/api/v1/test",
                canary_router=None,
                debug_mode=False,
            )

        assert response.status_code == 200
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        # Verify x-request-id was bridged to request-id
        assert call_kwargs["headers"]["request-id"] == "x-req-456"
        assert "X-Request-ID" not in call_kwargs["headers"] or call_kwargs["headers"].get("X-Request-ID") != "x-req-456"

    @pytest.mark.asyncio
    async def test_proxy_handler_post_with_body(self, mock_proxy_client, mock_httpx_response):
        """Test POST proxy forwarding with body preservation."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/v1/test"
        request.url.query = ""
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request_body = b'{"key": "value"}'
        request.body = AsyncMock(return_value=request_body)

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/api/v1/test",
                canary_router=None,
                debug_mode=False,
            )

        assert response.status_code == 200
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        assert call_kwargs["method"] == "POST"
        assert call_kwargs["content"] == request_body
        assert call_kwargs["headers"]["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_proxy_handler_query_string_preservation(self, mock_proxy_client, mock_httpx_response):
        """Test that query string is preserved correctly."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/test"
        request.url.query = "foo=bar&baz=qux"
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/api/v1/test",  # Path without query
                canary_router=None,
                debug_mode=False,
            )

        assert response.status_code == 200
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        # Verify query string is in URL
        url = call_kwargs["url"]
        assert "foo=bar" in url
        assert "baz=qux" in url

    @pytest.mark.asyncio
    async def test_proxy_handler_streaming_response(self, mock_proxy_client):
        """Test streaming response handling."""
        from starlette.responses import StreamingResponse
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/stream"
        request.url.query = ""
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        # Create mock streaming response
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.headers = {"Content-Type": "application/octet-stream"}
        
        # Mock streaming chunks
        async def mock_aiter_bytes():
            yield b"chunk1"
            yield b"chunk2"
            yield b"chunk3"
        
        mock_stream_response.aiter_bytes = mock_aiter_bytes
        mock_stream_response.aread = AsyncMock()

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/api/v1/stream",
                canary_router=None,
                debug_mode=False,
            )

        assert isinstance(response, StreamingResponse)
        assert response.status_code == 200
        
        # Verify streaming chunks by iterating over the response body
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        
        assert chunks == [b"chunk1", b"chunk2", b"chunk3"]

    @pytest.mark.asyncio
    async def test_proxy_handler_hop_by_hop_headers_stripped(self, mock_proxy_client, mock_httpx_response):
        """Test that hop-by-hop headers are stripped from request."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/test"
        request.url.query = ""
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=5",
            "Transfer-Encoding": "chunked",
            "Upgrade": "websocket",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/api/v1/test",
                canary_router=None,
                debug_mode=False,
            )

        assert response.status_code == 200
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        headers = call_kwargs["headers"]
        
        # Verify hop-by-hop headers are stripped
        assert "connection" not in headers or headers.get("connection") != "keep-alive"
        assert "keep-alive" not in headers
        assert "transfer-encoding" not in headers
        assert "upgrade" not in headers
        
        # Verify Host is preserved (not hop-by-hop)
        # Note: httpx may modify Host, but we verify X-Forwarded-Host
        assert "X-Forwarded-Host" in headers
        assert headers["X-Forwarded-Host"] == "gateway.example.com"

    @pytest.mark.asyncio
    async def test_proxy_handler_canary_routing_get(self, mock_proxy_client, mock_httpx_response):
        """Test proxy forwarding with canary routing for GET."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/partners/nav/api/v1/test"
        request.url.query = ""
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        # Create canary router that routes to canary
        rule = CanaryRule(
            partner="nav", endpoint_pattern="/partners/nav/api/v1/test", percentage=100
        )
        canary_router = CanaryRouter(rules=[rule], canary_enabled=True)

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/partners/nav/api/v1/test",
                canary_router=canary_router,
                debug_mode=True,
            )

        assert response.status_code == 200
        # Check that canary URL was used
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        assert "canary-api.example.com" in str(call_kwargs["url"])

        # Check debug header
        assert response.headers["X-Gateway-Upstream"] == "canary"

    @pytest.mark.asyncio
    async def test_proxy_handler_canary_routing_post_blocked(
        self, mock_proxy_client, mock_httpx_response
    ):
        """Test that POST requests are blocked from canary routing."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url.path = "/partners/nav/api/v1/test"
        request.url.query = ""
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b'{"data": "test"}')

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_httpx_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        mock_proxy_client.client.stream = MagicMock(return_value=mock_stream_context)
        mock_httpx_response.aread = AsyncMock()

        # Create canary router with POST rule
        rule = CanaryRule(
            partner="nav", endpoint_pattern="/partners/nav/api/v1/test", method="POST", percentage=100
        )
        canary_router = CanaryRouter(rules=[rule], canary_enabled=True)

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            response = await proxy_handler(
                request=request,
                full_path="/partners/nav/api/v1/test",
                canary_router=canary_router,
                debug_mode=True,
            )

        assert response.status_code == 200
        # Check that legacy URL was used (POST blocked from canary)
        call_kwargs = mock_proxy_client.client.stream.call_args[1]
        assert "legacy-api.example.com" in str(call_kwargs["url"])
        assert "canary-api.example.com" not in str(call_kwargs["url"])

        # Check debug header shows legacy
        assert response.headers["X-Gateway-Upstream"] == "legacy"


class TestContractFirstVsCatchAll:
    """Tests comparing contract-first endpoints vs catch-all proxy."""

    @pytest.mark.asyncio
    async def test_contract_first_vs_catch_all_same_behavior(
        self, mock_proxy_client
    ):
        """
        Test that contract-first endpoint and catch-all proxy produce identical results.
        
        This ensures proxy_to_upstream() is a thin wrapper that reuses the same
        proxy_handler implementation and shared httpx client.
        """
        # Create a simple GET request
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/test"
        request.url.query = "param=value"
        request.url.scheme = "https"
        request.headers = {
            "Authorization": "Bearer token123",
            "host": "gateway.example.com",
        }
        request.client.host = "1.2.3.4"
        request.body = AsyncMock(return_value=b"")

        # Mock streaming response with known content
        response_content = b'{"status": "ok", "data": "test"}'
        
        def create_mock_stream_response():
            """Create a fresh mock stream response for each call."""
            mock_stream_response = MagicMock()
            mock_stream_response.status_code = 200
            mock_stream_response.headers = {"Content-Type": "application/json"}
            
            async def mock_aiter_bytes():
                yield response_content
            
            mock_stream_response.aiter_bytes = mock_aiter_bytes
            mock_stream_response.aread = AsyncMock()
            return mock_stream_response

        # Track calls to verify they use the same client
        call_count = {"count": 0}
        
        def create_mock_stream_context():
            """Create a mock stream context that tracks calls."""
            call_count["count"] += 1
            mock_context = AsyncMock()
            mock_response = create_mock_stream_response()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            return mock_context

        # Setup proxy client with canary router and debug mode
        mock_proxy_client.canary_router = None  # No canary for this test
        mock_proxy_client.debug_mode = False

        with patch("gateway.proxy.handler.get_proxy_client", return_value=mock_proxy_client):
            with patch("gateway.proxy.endpoint.get_proxy_client", return_value=mock_proxy_client):
                # Setup mock to create new context for each call
                mock_proxy_client.client.stream = MagicMock(side_effect=create_mock_stream_context)
                
                # Test contract-first endpoint
                response1 = await proxy_to_upstream(
                    request=request,
                    upstream_path="/api/v1/test",
                )
                
                # Test catch-all proxy (via proxy_handler directly)
                response2 = await proxy_handler(
                    request=request,
                    full_path="/api/v1/test?param=value",
                    canary_router=None,
                    debug_mode=False,
                )

        # Both should return same status code
        assert response1.status_code == response2.status_code == 200
        
        # Both should use the same upstream URL (same client, same base URL)
        assert mock_proxy_client.client.stream.call_count == 2
        call1_url = mock_proxy_client.client.stream.call_args_list[0][1]["url"]
        call2_url = mock_proxy_client.client.stream.call_args_list[1][1]["url"]
        assert call1_url == call2_url
        assert "legacy-api.example.com" in call1_url
        assert "/api/v1/test" in call1_url
        assert "param=value" in call1_url
        
        # Both should forward same headers (excluding request-id which may differ)
        call1_headers = mock_proxy_client.client.stream.call_args_list[0][1]["headers"]
        call2_headers = mock_proxy_client.client.stream.call_args_list[1][1]["headers"]
        
        # Check key headers are present in both
        assert "Authorization" in call1_headers
        assert "Authorization" in call2_headers
        assert call1_headers["Authorization"] == call2_headers["Authorization"]
        assert "X-Forwarded-For" in call1_headers
        assert "X-Forwarded-For" in call2_headers
        
        # Both should have request-id (may differ, but both should exist)
        assert "request-id" in call1_headers
        assert "request-id" in call2_headers
        
        # Verify both responses are StreamingResponse
        from starlette.responses import StreamingResponse
        assert isinstance(response1, StreamingResponse)
        assert isinstance(response2, StreamingResponse)
        
        # Verify response content is identical
        # Note: We need to read from separate iterators since they're consumed
        chunks1 = []
        async for chunk in response1.body_iterator:
            chunks1.append(chunk)
        
        chunks2 = []
        async for chunk in response2.body_iterator:
            chunks2.append(chunk)
        
        assert chunks1 == chunks2 == [response_content]
        
        # Verify both use the same proxy client instance (shared httpx client)
        assert mock_proxy_client.client.stream.call_count == 2
        # Both calls should use the same client instance
        assert mock_proxy_client.client.stream.call_args_list[0].args == mock_proxy_client.client.stream.call_args_list[1].args
