from abc import ABC, abstractmethod
from enum import Enum


class LoginResult(Enum):
    SUCCESS = "SUCCESS"
    DATA_LIMIT = "DATA_LIMIT"
    FAILED = "FAILED"
    ERROR = "ERROR"


class BaseLoginStrategy(ABC):
    """Abstract base class for all captive portal authentication strategies."""

    def __init__(self, name="base"):
        self.name = name

    @abstractmethod
    def login(self, profile: dict, credentials: dict) -> LoginResult:
        """
        Execute authentication against the captive portal using profile details and credentials.
        Returns LoginResult.
        """
        pass
