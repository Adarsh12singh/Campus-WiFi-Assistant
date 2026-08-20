from core.strategies.playwright_strategy import PlaywrightStrategy
from core.strategies.http_strategy import HttpStrategy
from core.strategies.base import BaseLoginStrategy, LoginResult
from logger import write_log


class NoAuthStrategy(BaseLoginStrategy):
    """Fallback / No-authentication strategy for direct open networks."""
    def __init__(self):
        super().__init__(name="none")

    def login(self, profile: dict, credentials: dict) -> LoginResult:
        return LoginResult.SUCCESS


_STRATEGY_REGISTRY = {
    "playwright": PlaywrightStrategy,
    "http_post": HttpStrategy,
    "http": HttpStrategy,
    "none": NoAuthStrategy
}


def get_login_strategy(strategy_name: str) -> BaseLoginStrategy:
    """
    Factory to retrieve an instance of the requested login strategy.
    Defaults to PlaywrightStrategy if name is unrecognized.
    """
    key = (strategy_name or "playwright").lower()
    strategy_cls = _STRATEGY_REGISTRY.get(key, PlaywrightStrategy)
    return strategy_cls()
