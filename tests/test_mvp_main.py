"""Test per MVP v1 Main Agent."""

import pytest
from main_mvp import AIAgentMVP


class TestAIAgentMVP:
    """Test for AIAgentMVP."""

    def test_agent_creation(self):
        """Test creazione agente."""
        agent = AIAgentMVP(".")
        assert agent is not None
        assert agent.config is not None
        assert agent.model_orchestrator is not None
        assert agent.workflow is not None

    def test_agent_has_components(self):
        """Test che agente ha tutti i componenti."""
        agent = AIAgentMVP(".")
        
        assert hasattr(agent, 'bootstrap')
        assert hasattr(agent, 'config')
        assert hasattr(agent, 'model_orchestrator')
        assert hasattr(agent, 'workflow')
        assert hasattr(agent, 'roadmap')

    def test_config_manager(self):
        """Test config manager."""
        agent = AIAgentMVP(".")
        config = agent.config.get_system_config()
        
        assert config is not None
        assert config.ollama_url == "http://localhost:11434"

    def test_model_orchestrator(self):
        """Test model orchestrator."""
        agent = AIAgentMVP(".")
        
        assert len(agent.model_orchestrator.registry.models) > 0

    def test_workflow_orchestrator(self):
        """Test workflow orchestrator."""
        agent = AIAgentMVP(".")
        
        assert len(agent.workflow.workflows) == 0  # No workflows yet

    def test_roadmap_manager(self):
        """Test roadmap manager."""
        agent = AIAgentMVP(".")
        
        phases = agent.roadmap.get_all_phases()
        assert len(phases) == 11


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

