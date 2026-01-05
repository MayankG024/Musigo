"""Tests for rate limiting functionality"""

import pytest
from httpx import AsyncClient
from models.music import Song


@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting (when enabled)"""
    
    async def test_rate_limiting_disabled_in_tests(self, client: AsyncClient, sample_songs: list[Song]):
        """Test that rate limiting is disabled in test environment"""
        # Make multiple rapid requests - should not be rate limited
        for _ in range(10):
            response = await client.get("/api/music/search?q=test")
            assert response.status_code == 200
        
        # All requests should succeed without 429 Too Many Requests
    
    async def test_expensive_endpoints_work(self, client: AsyncClient, sample_songs: list[Song]):
        """Test that expensive endpoints work without rate limiting in tests"""
        # These would normally be rate limited to 10/minute
        response = await client.get("/api/discovery/discover?query=rock music")
        # May return 200 or error depending on external dependencies
        # Just verify it's not rate limited (429)
        assert response.status_code != 429
        
        response = await client.get(f"/api/discovery/recommendations/{sample_songs[0].id}")
        assert response.status_code != 429


@pytest.mark.asyncio
class TestRateLimitConfiguration:
    """Test rate limit configuration"""
    
    async def test_rate_limit_env_var(self):
        """Test that RATE_LIMIT_ENABLED is set to False in tests"""
        import os
        assert os.environ.get("RATE_LIMIT_ENABLED") == "False"
    
    async def test_rate_limit_config(self):
        """Test rate limit configuration from settings"""
        from api.core.config import settings
        assert settings.RATE_LIMIT_ENABLED is False
