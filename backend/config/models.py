from typing import TypedDict, Literal

ProviderType = Literal["gemini", "openrouter"]

class ModelInfo(TypedDict):
    provider: ProviderType
    display_name: str
    supports_judge: bool
    enabled: bool

MODEL_REGISTRY: dict[str, ModelInfo] = {
    "gemini-2.5-flash": {
        "provider": "gemini",
        "display_name": "Gemini 2.5 Flash",
        "supports_judge": True,
        "enabled": True,
    },
    "google/gemma-4-31b-it:free": {
        "provider": "openrouter",
        "display_name": "Gemma 4 31B",
        "supports_judge": True,
        "enabled": True,
    },
    "google/gemma-4-26b-a4b-it:free": {
        "provider": "openrouter",
        "display_name": "Gemma 4 26B",
        "supports_judge": True,
        "enabled": True,
    },
    "nvidia/nemotron-3-super-120b-a12b:free": {
        "provider": "openrouter",
        "display_name": "Nemotron Super",
        "supports_judge": True,
        "enabled": True,
    },
    "nvidia/nemotron-3-ultra-550b-a55b:free": {
        "provider": "openrouter",
        "display_name": "Nemotron Ultra",
        "supports_judge": True,
        "enabled": True,
    },
    "nvidia/nemotron-3-nano-30b-a3b:free": {
        "provider": "openrouter",
        "display_name": "Nemotron Nano",
        "supports_judge": True,
        "enabled": True,
    },
    "cohere/north-mini-code:free": {
        "provider": "openrouter",
        "supports_judge": True,
        "enabled": True,
    },
    "meta-llama/llama-3.1-8b-instruct:free": {
        "provider": "openrouter",
        "display_name": "Llama 3.1 8B",
        "supports_judge": True,
        "enabled": True,
    }
}
