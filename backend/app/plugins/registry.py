from __future__ import annotations

from app.modules.base import SecurityModule
from app.modules.port_probe import SafePortProbe
from app.modules.robots_checker import RobotsTxtChecker
from app.modules.security_txt_checker import SecurityTxtChecker
from app.modules.tech_fingerprint import TechnologyFingerprint
from app.modules.tls_analyzer import TlsAnalyzer
from app.modules.web_headers import WebSecurityHeadersAnalyzer
from app.schemas.modules import ModuleInfo


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, SecurityModule] = {}

    def register(self, module: SecurityModule) -> None:
        if not module.id or not module.name:
            raise ValueError("Module must define id and name")
        self._modules[module.id] = module

    def get(self, module_id: str) -> SecurityModule | None:
        return self._modules.get(module_id)

    def require(self, module_id: str) -> SecurityModule:
        module = self.get(module_id)
        if module is None:
            raise KeyError(f"Unknown module: {module_id}")
        return module

    def list(self) -> list[ModuleInfo]:
        return [module.info() for module in self._modules.values()]

    def ids(self) -> set[str]:
        return set(self._modules)


def build_default_registry() -> ModuleRegistry:
    registry = ModuleRegistry()
    registry.register(WebSecurityHeadersAnalyzer())
    registry.register(TlsAnalyzer())
    registry.register(RobotsTxtChecker())
    registry.register(SecurityTxtChecker())
    registry.register(TechnologyFingerprint())
    registry.register(SafePortProbe())
    return registry


module_registry = build_default_registry()

