"""Test per AI Model Layer."""

import pytest
from core.llm_models import (
    ModelType, TaskType, ModelConfig, PromptTemplate,
    ModelRegistry, ModelRouter, PromptManager,
    ModelOrchestrator, create_model_orchestrator
)


class TestModelRegistry:
    """Test ModelRegistry."""

    def test_registry_creation(self):
        """Test creazione registry."""
        registry = ModelRegistry()
        assert len(registry.models) > 0

    def test_get_model(self):
        """Test get modello."""
        registry = ModelRegistry()
        model = registry.get_model("qwen-4b")
        assert model is not None
        assert model.ollama_name == "qwen2:4b"

    def test_get_models_by_type(self):
        """Test get per tipo."""
        registry = ModelRegistry()
        coding_models = registry.get_models_by_type(ModelType.CODING)
        assert len(coding_models) >= 1

    def test_can_fit_in_vram(self):
        """Test modelli per VRAM."""
        registry = ModelRegistry()
        models = registry.can_fit_in_vram(8.0)
        assert len(models) > 0
        for m in models:
            assert m.vram_required_gb <= 8.0


class TestModelRouter:
    """Test ModelRouter."""

    def test_router_creation(self):
        """Test creazione router."""
        registry = ModelRegistry()
        router = ModelRouter(registry)
        assert router.available_vram_gb == 16.0

    def test_select_model_for_coding(self):
        """Test selezione modello coding."""
        registry = ModelRegistry()
        router = ModelRouter(registry)
        
        model = router.select_model(TaskType.IMPLEMENTATION, "coder")
        assert model is not None
        assert model.model_type == ModelType.CODING

    def test_select_model_for_planning(self):
        """Test selezione modello planning."""
        registry = ModelRegistry()
        router = ModelRouter(registry)
        
        model = router.select_model(TaskType.ORCHESTRATION, "planner")
        assert model is not None
        assert model.model_type == ModelType.ROUTING

    def test_select_model_vram_limit(self):
        """Test limite VRAM."""
        registry = ModelRegistry()
        router = ModelRouter(registry, available_vram_gb=3.0)
        
        model = router.select_model(TaskType.IMPLEMENTATION, "coder")
        assert model is None or model.vram_required_gb <= 3.0


class TestPromptManager:
    """Test PromptManager."""

    def test_manager_creation(self):
        """Test creazione manager."""
        manager = PromptManager()
        assert len(manager.prompts) > 0

    def test_get_prompt(self):
        """Test get prompt."""
        manager = PromptManager()
        prompt = manager.get_prompt("architect")
        assert prompt is not None
        assert prompt.role == "Software Architect"

    def test_render_prompt(self):
        """Test render prompt."""
        manager = PromptManager()
        rendered = manager.render_prompt(
            "architect",
            {},
            "Add authentication to system"
        )
        assert "Software Architect" in rendered
        assert "Add authentication" in rendered

    def test_all_prompts_registered(self):
        """Test che tutti i prompt sono registrati."""
        manager = PromptManager()
        prompts = ["architect", "planner", "coder", "reviewer", "tester"]
        for p in prompts:
            assert manager.get_prompt(p) is not None


class TestModelOrchestrator:
    """Test ModelOrchestrator."""

    def test_orchestrator_creation(self):
        """Test creazione orchestratore."""
        orch = create_model_orchestrator()
        assert orch.call_count == 0
        assert orch.token_count == 0

    def test_get_model_for_task(self):
        """Test get modello per task."""
        orch = create_model_orchestrator()
        
        model = orch.get_model_for_task(TaskType.IMPLEMENTATION, "coder")
        assert model is not None

    def test_get_prompt_for_agent(self):
        """Test get prompt per agente."""
        orch = create_model_orchestrator()
        
        prompt = orch.get_prompt_for_agent("coder")
        assert prompt is not None

    def test_record_call(self):
        """Test registrazione chiamate."""
        orch = create_model_orchestrator()
        
        orch.record_call(150)
        assert orch.call_count == 1
        assert orch.token_count == 150

    def test_get_stats(self):
        """Test statistiche."""
        orch = create_model_orchestrator()
        
        orch.record_call(100)
        orch.record_call(200)
        
        stats = orch.get_stats()
        assert stats["calls"] == 2
        assert stats["total_tokens"] == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

