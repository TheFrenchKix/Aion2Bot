from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class Detection:
    x1: float
    y1: float
    x2: float
    y2: float
    score: float
    cls: int
    label: str

    @property
    def center(self) -> tuple[float, float]:
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2


class Detector(ABC):
    names: dict[int, str] = {}

    @abstractmethod
    def predict(self, frame_bgr: np.ndarray) -> list[Detection]:
        """Coordonnees retournees dans le repere de la frame d'origine."""


class NullDetector(Detector):
    """Sans modele : permet de mesurer / tester la capture seule."""

    def predict(self, frame_bgr: np.ndarray) -> list[Detection]:
        return []
