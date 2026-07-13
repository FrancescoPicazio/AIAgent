"""Test per Development Roadmap."""

import pytest
from core.development_roadmap import (
    Phase, Priority, Component, PhaseDefinition,
    RoadmapManager, create_roadmap_manager
)


class TestPhase:
    """Test Phase enum."""

    def test_phase_values(self):
        """Test valori phase."""
        assert Phase.PHASE_0.value == "phase_0_environment"
        assert Phase.PHASE_1.value == "phase_1_basic_agent"
        assert len(Phase) == 11


class TestComponent:
    """Test Component."""

    def test_component_creation(self):
        """Test creazione component."""
        comp = Component(
            name="Test Component",
            description="Test description",
            complexity="low"
        )
        assert comp.name == "Test Component"
        assert comp.dependencies == []


class TestRoadmapManager:
    """Test RoadmapManager."""

    def test_roadmap_creation(self):
        """Test creazione roadmap."""
        rm = create_roadmap_manager()
        assert rm is not None
        assert len(rm.phases) == 11

    def test_get_phase(self):
        """Test get fase."""
        rm = create_roadmap_manager()
        phase = rm.get_phase(Phase.PHASE_0)
        
        assert phase is not None
        assert phase.title == "Ambiente locale"
        assert phase.priority == Priority.CRITICAL

    def test_get_all_phases(self):
        """Test get all fasi."""
        rm = create_roadmap_manager()
        phases = rm.get_all_phases()
        
        assert len(phases) == 11
        assert phases[0].phase == Phase.PHASE_0
        assert phases[10].phase == Phase.PHASE_10

    def test_phase_dependencies(self):
        """Test catena dipendenze."""
        rm = create_roadmap_manager()
        
        # Verifica che ogni fase (tranne ultima) ha una next_phase
        for i, phase_def in enumerate(rm.get_all_phases()[:-1]):
            assert phase_def.next_phase is not None

    def test_success_criteria(self):
        """Test criteri di successo."""
        rm = create_roadmap_manager()
        phase = rm.get_phase(Phase.PHASE_1)
        
        assert len(phase.success_criteria) > 0
        assert all(isinstance(c, str) for c in phase.success_criteria)

    def test_get_estimated_total_days(self):
        """Test calcolo giorni totali."""
        rm = create_roadmap_manager()
        total_days = rm.get_estimated_total_days()
        
        assert total_days > 0
        assert isinstance(total_days, int)

    def test_get_priority_ranking(self):
        """Test ranking per priorità."""
        rm = create_roadmap_manager()
        ranking = rm.get_priority_ranking()
        
        assert len(ranking) > 0
        # Verifica che sia ordinato per priorità
        for i in range(len(ranking) - 1):
            assert ranking[i][1] >= ranking[i+1][1]

    def test_components_structure(self):
        """Test struttura componenti."""
        rm = create_roadmap_manager()
        
        for phase_def in rm.get_all_phases():
            assert len(phase_def.components) > 0
            for comp in phase_def.components:
                assert hasattr(comp, 'name')
                assert hasattr(comp, 'complexity')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

