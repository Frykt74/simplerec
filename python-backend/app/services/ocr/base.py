from abc import ABC, abstractmethod
import numpy as np
from typing import Dict

class BaseOCR(ABC):
    @abstractmethod
    def recognize_printed(self, image: np.ndarray) -> Dict: ...
    @abstractmethod
    def recognize_handwritten(self, image: np.ndarray) -> Dict: ...
