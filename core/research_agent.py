"""
Research Agent - Knowledge Acquisition & Analysis.

Researches technologies, analyzes documentation, and maintains knowledge base.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Types of knowledge sources."""
    OFFICIAL_DOCS = "official_docs"
    OFFICIAL_REPO = "official_repo"
    ARTICLE = "article"
    FORUM = "forum"
    CODE_EXAMPLE = "code_example"
    PAPER = "paper"
    INTERNAL = "internal"


class ResearchStatus(Enum):
    """Status of a research task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchSource:
    """Represents a knowledge source."""
    source_id: str
    source_type: SourceType
    title: str
    url: Optional[str] = None
    content: Optional[str] = None
    relevance_score: float = 0.0
    trusted: bool = False


@dataclass
class ResearchFinding:
    """Represents a research finding."""
    finding_id: str
    topic: str
    claim: str
    sources: List[ResearchSource] = field(default_factory=list)
    confidence_score: float = 0.0  # 0.0-1.0
    validation_status: str = "unvalidated"
    extracted_at: str = ""


@dataclass
class TechnologyComparison:
    """Technology comparison analysis."""
    comparison_id: str
    technologies: List[str]
    criteria: Dict[str, List[str]] = field(default_factory=dict)
    scores: Dict[str, Dict[str, float]] = field(default_factory=dict)
    recommendation: Optional[str] = None
    reasoning: str = ""


class ResearchTrigger:
    """
    Determines when research is needed.
    """

    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize research trigger.
        
        Args:
            confidence_threshold: Threshold for triggering research (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        logger.info(f"Research trigger initialized (threshold: {confidence_threshold})")

    def should_research(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if research is needed.
        
        Args:
            context: Context dict with agent knowledge
            
        Returns:
            (should_research, reason)
        """
        reasons = []
        confidence = 1.0

        # Check for unknown library
        if context.get("unknown_library"):
            reasons.append("Unknown library encountered")
            confidence *= 0.5

        # Check for unknown architecture
        if context.get("unknown_architecture"):
            reasons.append("Unknown architecture pattern")
            confidence *= 0.6

        # Check for external dependencies
        if context.get("external_dependency"):
            reasons.append("External dependency needed")
            confidence *= 0.7

        # Check for explicit knowledge gap
        if context.get("knowledge_gap"):
            reasons.append("Knowledge gap identified")
            confidence *= 0.3

        # Check agent confidence
        if "confidence" in context:
            confidence = min(confidence, context["confidence"])

        should_research = confidence < self.confidence_threshold

        reason = "; ".join(reasons) if reasons else "High confidence in current knowledge"

        logger.info(f"Research trigger: {should_research} (confidence: {confidence:.2f})")

        return should_research, reason


class ResearchAgent:
    """
    Research Agent for knowledge acquisition.
    
    Searches for information, validates sources, and updates knowledge base.
    """

    def __init__(self):
        """Initialize research agent."""
        self.trigger = ResearchTrigger(confidence_threshold=0.7)
        self.findings: Dict[str, ResearchFinding] = {}
        self.comparisons: Dict[str, TechnologyComparison] = {}
        self.trusted_sources = [
            SourceType.OFFICIAL_DOCS,
            SourceType.OFFICIAL_REPO,
            SourceType.PAPER
        ]
        
        logger.info("Research agent initialized")

    def research_topic(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """
        Research a specific topic.
        
        Args:
            topic: Topic to research
            depth: Research depth (shallow, medium, deep)
            
        Returns:
            Research results
        """
        logger.info(f"Researching: {topic} (depth: {depth})")

        findings = []
        sources_checked = 0

        # Simulate research process
        # In production: search documentation, repos, web, papers

        # Generate findings
        for i in range(3):
            finding = ResearchFinding(
                finding_id=f"{topic}_{i}",
                topic=topic,
                claim=f"Finding {i+1} about {topic}",
                confidence_score=0.8 + (i * 0.05),
                validation_status="validated",
                extracted_at=datetime.now().isoformat()
            )
            findings.append(finding)
            self.findings[finding.finding_id] = finding
            sources_checked += 2

        return {
            "topic": topic,
            "findings": len(findings),
            "sources_checked": sources_checked,
            "confidence": 0.85,
            "status": "completed",
            "findings_detail": [
                {
                    "id": f.finding_id,
                    "claim": f.claim,
                    "confidence": f.confidence_score
                }
                for f in findings
            ]
        }

    def compare_technologies(self, technologies: List[str], criteria: List[str]) -> Dict[str, Any]:
        """
        Compare multiple technologies.
        
        Args:
            technologies: List of technologies to compare
            criteria: Comparison criteria
            
        Returns:
            Comparison analysis
        """
        logger.info(f"Comparing technologies: {', '.join(technologies)}")

        comparison_id = f"comp_{len(self.comparisons)}"
        
        # Simulate scoring (0.0-1.0)
        scores = {}
        for tech in technologies:
            scores[tech] = {criterion: 0.5 + (hash(f"{tech}_{criterion}") % 50) / 100 
                          for criterion in criteria}

        # Recommend best option
        best_tech = max(technologies, 
                       key=lambda t: sum(scores[t].values()) / len(criteria))

        comparison = TechnologyComparison(
            comparison_id=comparison_id,
            technologies=technologies,
            criteria={f"criterion_{i}": criteria for i in range(len(criteria))},
            scores=scores,
            recommendation=best_tech,
            reasoning=f"{best_tech} scores highest across all criteria"
        )

        self.comparisons[comparison_id] = comparison

        return {
            "comparison_id": comparison_id,
            "technologies": technologies,
            "scores": scores,
            "recommendation": best_tech,
            "reasoning": comparison.reasoning
        }

    def validate_information(self, claim: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a claim against multiple sources.
        
        Args:
            claim: Claim to validate
            sources: List of source metadata
            
        Returns:
            Validation result with confidence score
        """
        logger.info(f"Validating claim: {claim}")

        # Count source types
        trusted_count = sum(1 for s in sources if s.get("trusted", False))
        total_sources = len(sources)

        # Calculate confidence
        confidence = 0.5 + (trusted_count / max(total_sources, 1)) * 0.5

        validation_status = "validated" if confidence > 0.7 else "unvalidated"

        return {
            "claim": claim,
            "total_sources": total_sources,
            "trusted_sources": trusted_count,
            "confidence_score": confidence,
            "validation_status": validation_status,
            "recommendation": "Accept" if confidence > 0.7 else "Needs review"
        }

    def generate_research_report(self, topic: str, findings: List[ResearchFinding]) -> str:
        """
        Generate a research report.
        
        Args:
            topic: Research topic
            findings: Research findings
            
        Returns:
            Report as markdown
        """
        report = f"# Research Report: {topic}\n\n"
        report += f"**Generated:** {datetime.now().isoformat()}\n\n"

        report += "## Findings\n\n"
        for finding in findings:
            report += f"### {finding.claim}\n"
            report += f"- Confidence: {finding.confidence_score:.1%}\n"
            report += f"- Status: {finding.validation_status}\n\n"

        report += "## Conclusion\n\n"
        report += f"Research depth complete. Found {len(findings)} validated findings.\n"

        return report

    def update_knowledge_base(self, finding_id: str, knowledge_base: Dict[str, Any]) -> bool:
        """
        Update knowledge base with a finding.
        
        Args:
            finding_id: Finding to add
            knowledge_base: Target knowledge base dict
            
        Returns:
            Success status
        """
        finding = self.findings.get(finding_id)
        if not finding:
            logger.warning(f"Finding not found: {finding_id}")
            return False

        if finding.confidence_score < 0.7:
            logger.warning(f"Finding confidence too low: {finding.confidence_score}")
            return False

        # Add to knowledge base
        if finding.topic not in knowledge_base:
            knowledge_base[finding.topic] = []

        knowledge_base[finding.topic].append({
            "claim": finding.claim,
            "confidence": finding.confidence_score,
            "timestamp": finding.extracted_at,
            "status": finding.validation_status
        })

        logger.info(f"Knowledge base updated with: {finding_id}")
        return True

    def get_research_status(self) -> Dict[str, Any]:
        """Get research agent status."""
        return {
            "total_findings": len(self.findings),
            "total_comparisons": len(self.comparisons),
            "trusted_sources": len(self.trusted_sources),
            "confidence_threshold": self.trigger.confidence_threshold,
            "findings": list(self.findings.keys()),
            "comparisons": list(self.comparisons.keys())
        }


def create_research_agent() -> ResearchAgent:
    """Factory function."""
    return ResearchAgent()

