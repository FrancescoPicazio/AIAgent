"""Test per Research Agent."""

import pytest
from core.research_agent import (
    SourceType, ResearchStatus, ResearchSource, ResearchFinding,
    TechnologyComparison, ResearchTrigger, ResearchAgent, create_research_agent
)


class TestResearchTrigger:
    """Test ResearchTrigger."""

    def test_trigger_creation(self):
        """Test creazione trigger."""
        trigger = ResearchTrigger()
        assert trigger is not None
        assert trigger.confidence_threshold == 0.7

    def test_trigger_no_research_needed(self):
        """Test trigger quando research non serve."""
        trigger = ResearchTrigger(0.7)
        context = {}
        
        should_research, reason = trigger.should_research(context)
        
        assert should_research is False

    def test_trigger_research_needed_unknown_lib(self):
        """Test trigger con libreria sconosciuta."""
        trigger = ResearchTrigger(0.7)
        context = {"unknown_library": True}
        
        should_research, reason = trigger.should_research(context)
        
        assert should_research is True
        assert "Unknown library" in reason

    def test_trigger_research_with_confidence(self):
        """Test trigger con confidence bassa."""
        trigger = ResearchTrigger(0.7)
        context = {"confidence": 0.5}
        
        should_research, reason = trigger.should_research(context)
        
        assert should_research is True


class TestResearchFinding:
    """Test ResearchFinding."""

    def test_finding_creation(self):
        """Test creazione finding."""
        finding = ResearchFinding(
            finding_id="f1",
            topic="async",
            claim="Python supports async/await",
            confidence_score=0.95
        )
        
        assert finding.finding_id == "f1"
        assert finding.confidence_score == 0.95


class TestResearchAgent:
    """Test ResearchAgent."""

    def test_agent_creation(self):
        """Test creazione agente."""
        agent = create_research_agent()
        assert agent is not None
        assert isinstance(agent, ResearchAgent)

    def test_research_topic(self):
        """Test ricerca topic."""
        agent = create_research_agent()
        result = agent.research_topic("async", depth="medium")
        
        assert result["status"] == "completed"
        assert result["findings"] > 0
        assert "confidence" in result

    def test_compare_technologies(self):
        """Test confronto tecnologie."""
        agent = create_research_agent()
        result = agent.compare_technologies(
            ["Redis", "Memcached"],
            ["performance", "simplicity"]
        )
        
        assert "recommendation" in result
        assert result["recommendation"] in ["Redis", "Memcached"]

    def test_validate_information(self):
        """Test validazione informazione."""
        agent = create_research_agent()
        sources = [
            {"trusted": True},
            {"trusted": True},
            {"trusted": False}
        ]
        
        result = agent.validate_information("Test claim", sources)
        
        assert "confidence_score" in result
        assert result["total_sources"] == 3
        assert result["trusted_sources"] == 2

    def test_generate_research_report(self):
        """Test generazione report."""
        agent = create_research_agent()
        
        finding = ResearchFinding(
            finding_id="f1",
            topic="test",
            claim="Test claim",
            confidence_score=0.9
        )
        agent.findings["f1"] = finding
        
        report = agent.generate_research_report("test", [finding])
        
        assert "# Research Report:" in report
        assert "test claim" in report.lower()

    def test_update_knowledge_base(self):
        """Test aggiornamento knowledge base."""
        agent = create_research_agent()
        
        finding = ResearchFinding(
            finding_id="f1",
            topic="async",
            claim="Async is good",
            confidence_score=0.9
        )
        agent.findings["f1"] = finding
        
        kb = {}
        result = agent.update_knowledge_base("f1", kb)
        
        assert result is True
        assert "async" in kb

    def test_get_research_status(self):
        """Test get status."""
        agent = create_research_agent()
        agent.research_topic("test")
        
        status = agent.get_research_status()
        
        assert status["total_findings"] > 0
        assert "confidence_threshold" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

