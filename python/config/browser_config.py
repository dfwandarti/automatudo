# python/config/browser_config.py
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class BrowserConfig:
    """Carrega configuração de browser/viewport do arquivo de config"""

    _config: Dict[str, Any] = {}
    _loaded: bool = False
    _default_device: str = "mobile"

    @classmethod
    def _load_config(cls) -> None:
        """Carrega o arquivo browser_config.json"""
        if cls._loaded:
            return

        try:
            # Tentar carregar desde o diretório raiz do projeto
            config_path = Path(__file__).parent.parent.parent / "browser_config.json"

            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    cls._config = json.load(f)
            else:
                print(f"[Warning] Config file not found at {config_path}. Using defaults.")
                cls._config = {"desktop": {"name": "Desktop", "viewport": {"width": 1920, "height": 1080}}}
        except Exception as e:
            print(f"[Error] Failed to load browser config: {e}")
            cls._config = {"desktop": {"name": "Desktop", "viewport": {"width": 1920, "height": 1080}}}

        cls._loaded = True

    @classmethod
    def get_device_type(cls) -> str:
        """Retorna o tipo de device (desktop/mobile/tablet)

        Priority:
        1. Variável de ambiente BROWSER_DEVICE
        2. Valor padrão (desktop)
        """
        device = os.getenv("BROWSER_DEVICE", cls._default_device).lower()
        return device

    @classmethod
    def is_responsive(cls) -> bool:
        device = cls.get_device_type()
        return device in ["mobile", "tablet"]

    @classmethod
    def get_config(cls, device_type: Optional[str] = None) -> Dict[str, Any]:
        """Retorna a configuração do browser para o device especificado

        Args:
            device_type: tipo de device (desktop/mobile/tablet).
                        Se None, lê da variável de ambiente ou usa default.

        Returns:
            Dict com 'viewport', 'device_scale_factor', 'is_mobile', etc.
        """
        cls._load_config()

        if device_type is None:
            device_type = cls.get_device_type()

        config = cls._config.get(device_type, {})
        if not config:
            print(f"[Warning] Device '{device_type}' not found. Using 'desktop'.")
            config = cls._config.get("desktop", {})

        return config

    @classmethod
    def get_viewport(cls, device_type: Optional[str] = None) -> Dict[str, int]:
        """Retorna apenas o viewport {width, height}"""
        config = cls.get_config(device_type)
        return config.get("viewport", {"width": 1920, "height": 1080})

    @classmethod
    def get_device_name(cls, device_type: Optional[str] = None) -> str:
        """Retorna o nome amigável do device"""
        config = cls.get_config(device_type)
        return config.get("name", "Unknown")

    @classmethod
    def get_all_devices(cls) -> list:
        """Retorna lista de tipos de devices disponíveis"""
        cls._load_config()
        return list(cls._config.keys())

    @classmethod
    def print_config_info(cls) -> None:
        """Imprime informações de configuração no console (debug)"""
        device = cls.get_device_type()
        config = cls.get_config(device)
        print(f"\n{'='*60}")
        print(f"[Browser Config] Device Type: {device}")
        print(f"[Browser Config] Name: {config.get('name', 'Unknown')}")
        print(f"[Browser Config] Viewport: {config.get('viewport', {})}")
        print(f"[Browser Config] Mobile: {config.get('is_mobile', False)}")
        print(f"{'='*60}\n")

    @classmethod
    def get_device_type(cls) -> str:
        """Retorna o tipo de device (desktop/mobile/tablet)

        Priority:
        1. Variável de ambiente BROWSER_DEVICE
        2. Valor padrão (mobile)
        """
        return cls._default_device