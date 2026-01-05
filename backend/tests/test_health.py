"""Tests for health check endpoints"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_basic_health_check(self, client: AsyncClient):
        """Test basic health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        # Environment may be "development" or "test" depending on settings
        assert data["environment"] in ["test", "development"]
        assert "checks" in data
        assert data["checks"]["api"] == "up"
    
    async def test_liveness_probe(self, client: AsyncClient):
        """Test Kubernetes liveness probe"""
        response = await client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data
    
    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check with database"""
        response = await client.get("/ready")
        
        # May be 503 if vector store or Redis not available
        # In test environment with REQUIRE_CHROMA=False, should be 200
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "ready" in data
        assert "checks" in data
        assert "database" in data["checks"]
    
    async def test_startup_probe(self, client: AsyncClient):
        """Test Kubernetes startup probe"""
        response = await client.get("/health/startup")
        
        # May be 503 if dependencies not ready
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "startup_complete" in data
        assert "checks" in data
