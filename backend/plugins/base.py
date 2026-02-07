from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional


@dataclass
class PluginContext:
    device: str = "cpu"
    consciousness_state: Optional[Dict[str, Any]] = None


class PluginBase(ABC):
    plugin_name: str
    model_id: str

    def __init__(self, context: PluginContext) -> None:
        self.context = context
        self.model = None

    @abstractmethod
    def load_model(self) -> None:
        """Load plugin model/resources."""

    @abstractmethod
    def run(self, text: str) -> Dict[str, Any]:
        """Run plugin inference."""

    @contextmanager
    def isolated_cuda(self) -> Iterator[None]:
        """Best-effort CUDA memory isolation between plugin runs."""
        try:
            import torch

            if self.context.device.startswith("cuda"):
                torch.cuda.empty_cache()
            yield
            if self.context.device.startswith("cuda"):
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
        except Exception:
            yield
