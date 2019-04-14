from abc import ABC, abstractmethod
from typing import Dict


class BaseCQ(ABC):
    """Base command/query class for use case."""

    @abstractmethod
    def execute(self, request: Dict = None):
        """Execute query"""
