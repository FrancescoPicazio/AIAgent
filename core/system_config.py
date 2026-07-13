"""
System Configuration and Bootstrap.

Central configuration management for the AI Agent system.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configurazione di un modello."""
    name: str
    ollama_name: str
    temperature: float = 0.3
    max_tokens: int = 2048
    vram_required_gb: float = 4.0


@dataclass
class SystemConfig:
    """Configurazione generale del sistema."""
    project_root: Path
    ai_folder: Path
    max_retries: int = 5
    timeout_seconds: int = 300
    log_level: str = "INFO"
    ollama_url: str = "http://localhost:11434"
    enable_langsmith: bool = False
    langsmith_api_key: Optional[str] = None


class ConfigManager:
    """
    Gestore centralizzato della configurazione.
    """

    def __init__(self, project_root: str = None):
        """
        Inizializza config manager.
        
        Args:
            project_root: Root del progetto
        """
        self.project_root = Path(project_root or os.getcwd())
        self.ai_folder = self.project_root / ".ai"
        self.config_folder = self.ai_folder / "config"
        
        # Crea folder se non esistono
        self.ai_folder.mkdir(exist_ok=True)
        self.config_folder.mkdir(exist_ok=True)
        
        self.system_config = self._load_system_config()
        self.model_configs = self._load_model_configs()

    def _load_system_config(self) -> SystemConfig:
        """Carica configurazione sistema."""
        env_ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        env_max_retries = int(os.getenv("MAX_RETRIES", "5"))
        env_log_level = os.getenv("LOG_LEVEL", "INFO")
        env_langsmith = os.getenv("LANGSMITH_API_KEY")
        
        return SystemConfig(
            project_root=self.project_root,
            ai_folder=self.ai_folder,
            max_retries=env_max_retries,
            log_level=env_log_level,
            ollama_url=env_ollama_url,
            enable_langsmith=env_langsmith is not None,
            langsmith_api_key=env_langsmith,
        )

    def _load_model_configs(self) -> Dict[str, ModelConfig]:
        """Carica configurazione modelli."""
        configs = {
            "router": ModelConfig(
                name="qwen-4b",
                ollama_name="qwen2:4b",
                temperature=0.2,
                vram_required_gb=4.0
            ),
            "coder": ModelConfig(
                name="qwen-coder-14b",
                ollama_name="qwen2-coder:14b",
                temperature=0.1,
                vram_required_gb=10.0
            ),
            "reasoning": ModelConfig(
                name="gemma-reasoning",
                ollama_name="gemma:latest",
                temperature=0.3,
                vram_required_gb=8.0
            ),
        }
        
        # Carica da file se esiste
        models_file = self.config_folder / "models.json"
        if models_file.exists():
            try:
                with open(models_file) as f:
                    custom_configs = json.load(f)
                    for key, config_data in custom_configs.items():
                        configs[key] = ModelConfig(**config_data)
                logger.info(f"Loaded custom models config from {models_file}")
            except Exception as e:
                logger.warning(f"Error loading custom models config: {e}")
        
        return configs

    def get_system_config(self) -> SystemConfig:
        """Ritorna configurazione sistema."""
        return self.system_config

    def get_model_config(self, model_type: str) -> Optional[ModelConfig]:
        """Ritorna configurazione modello."""
        return self.model_configs.get(model_type)

    def get_all_model_configs(self) -> Dict[str, ModelConfig]:
        """Ritorna tutte le configurazioni modelli."""
        return self.model_configs.copy()

    def save_model_config(self, model_type: str, config: ModelConfig):
        """Salva configurazione modello."""
        self.model_configs[model_type] = config
        
        # Salva su file
        models_file = self.config_folder / "models.json"
        configs_dict = {
            k: {
                "name": v.name,
                "ollama_name": v.ollama_name,
                "temperature": v.temperature,
                "max_tokens": v.max_tokens,
                "vram_required_gb": v.vram_required_gb,
            }
            for k, v in self.model_configs.items()
        }
        
        with open(models_file, "w") as f:
            json.dump(configs_dict, f, indent=2)
        
        logger.info(f"Saved model config for {model_type}")

    def setup_logging(self):
        """Configura logging."""
        log_level = getattr(logging, self.system_config.log_level, logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        logger.info(f"Logging configured at level {self.system_config.log_level}")


class SystemBootstrap:
    """
    Bootstrap del sistema.
    
    Inizializza tutti i componenti.
    """

    def __init__(self, project_root: str = None):
        """Inizializza bootstrap."""
        self.config_manager = ConfigManager(project_root)
        self.config_manager.setup_logging()

    def get_config_manager(self) -> ConfigManager:
        """Ritorna config manager."""
        return self.config_manager

    def validate_environment(self) -> Dict[str, bool]:
        """
        Valida l'ambiente.
        
        Returns:
            Dict con status di ogni controllo
        """
        checks = {
            "project_root_exists": self.config_manager.project_root.exists(),
            "ai_folder_exists": self.config_manager.ai_folder.exists(),
            ".env_exists": (self.config_manager.project_root / ".env").exists(),
        }

        # Controlla Ollama (opzionale)
        try:
            import requests
            url = f"{self.config_manager.system_config.ollama_url}/api/tags"
            response = requests.get(url, timeout=2)
            checks["ollama_available"] = response.status_code == 200
        except Exception:
            checks["ollama_available"] = False

        logger.info(f"Environment validation: {checks}")
        return checks

    def initialize_directories(self):
        """Inizializza directory necessarie."""
        directories = [
            self.config_manager.ai_folder,
            self.config_manager.ai_folder / "memory",
            self.config_manager.ai_folder / "knowledge",
            self.config_manager.ai_folder / "graph",
            self.config_manager.ai_folder / "vector",
            self.config_manager.ai_folder / "prompts",
            self.config_manager.ai_folder / "logs",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {directory}")

    def print_config_summary(self):
        """Stampa sommario configurazione."""
        config = self.config_manager.system_config
        
        print("\n" + "="*60)
        print("AI SOFTWARE ENGINEER AGENT - CONFIGURATION SUMMARY")
        print("="*60)
        print(f"Project Root: {config.project_root}")
        print(f"AI Folder: {config.ai_folder}")
        print(f"Ollama URL: {config.ollama_url}")
        print(f"Max Retries: {config.max_retries}")
        print(f"Timeout: {config.timeout_seconds}s")
        print(f"Log Level: {config.log_level}")
        print(f"LangSmith: {'Enabled' if config.enable_langsmith else 'Disabled'}")
        
        print("\nModels:")
        for model_type, model_config in self.config_manager.get_all_model_configs().items():
            print(f"  {model_type}: {model_config.ollama_name} ({model_config.vram_required_gb}GB VRAM)")
        
        print("="*60 + "\n")


def create_bootstrap(project_root: str = None) -> SystemBootstrap:
    """Factory function."""
    return SystemBootstrap(project_root)

