"""Test per System Configuration."""

import pytest
import tempfile
from pathlib import Path
from core.system_config import (
    ModelConfig, SystemConfig, ConfigManager,
    SystemBootstrap, create_bootstrap
)


class TestModelConfig:
    """Test ModelConfig."""

    def test_model_config_creation(self):
        """Test creazione config modello."""
        config = ModelConfig(
            name="test-model",
            ollama_name="test:latest",
            temperature=0.2
        )
        assert config.name == "test-model"
        assert config.temperature == 0.2


class TestConfigManager:
    """Test ConfigManager."""

    def test_config_manager_creation(self):
        """Test creazione config manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            assert manager.project_root == Path(tmpdir)
            assert manager.ai_folder.exists()

    def test_get_system_config(self):
        """Test get system config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            config = manager.get_system_config()
            assert config is not None
            assert config.ollama_url == "http://localhost:11434"

    def test_get_model_config(self):
        """Test get model config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            config = manager.get_model_config("router")
            assert config is not None
            assert config.ollama_name == "qwen2:4b"

    def test_get_all_model_configs(self):
        """Test get all model configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            configs = manager.get_all_model_configs()
            assert len(configs) >= 3
            assert "router" in configs
            assert "coder" in configs

    def test_save_and_load_model_config(self):
        """Test save e load config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            # Salva
            new_config = ModelConfig(
                name="custom",
                ollama_name="custom:7b",
                temperature=0.5
            )
            manager.save_model_config("custom", new_config)
            
            # Carica
            manager2 = ConfigManager(tmpdir)
            loaded = manager2.get_model_config("custom")
            assert loaded is not None
            assert loaded.ollama_name == "custom:7b"


class TestSystemBootstrap:
    """Test SystemBootstrap."""

    def test_bootstrap_creation(self):
        """Test creazione bootstrap."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = create_bootstrap(tmpdir)
            assert bootstrap is not None

    def test_validate_environment(self):
        """Test validazione ambiente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = create_bootstrap(tmpdir)
            checks = bootstrap.validate_environment()
            
            assert "project_root_exists" in checks
            assert "ai_folder_exists" in checks
            assert checks["project_root_exists"] is True

    def test_initialize_directories(self):
        """Test inizializzazione directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = create_bootstrap(tmpdir)
            bootstrap.initialize_directories()
            
            memory_dir = Path(tmpdir) / ".ai" / "memory"
            assert memory_dir.exists()

    def test_get_config_manager(self):
        """Test get config manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = create_bootstrap(tmpdir)
            manager = bootstrap.get_config_manager()
            assert manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

